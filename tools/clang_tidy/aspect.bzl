load("@rules_cc//cc:action_names.bzl", "CPP_COMPILE_ACTION_NAME")
load("@rules_cc//cc:find_cc_toolchain.bzl", "find_cc_toolchain", "use_cc_toolchain")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")

def _create_full_cc_compilation_context(target, ctx):
    # Because of the bug described in https://github.com/bazelbuild/bazel/issues/19663 we need an own compilation
    # context not ignoring the implementation_deps
    target_cc = target[CcInfo].compilation_context

    if hasattr(ctx.rule.attr, "implementation_deps"):
        defines = depset(transitive = [target_cc.defines, target_cc.local_defines] + [dep[CcInfo].compilation_context.defines for dep in ctx.rule.attr.implementation_deps])

        includes = depset(transitive = [target_cc.includes] + [dep[CcInfo].compilation_context.includes for dep in ctx.rule.attr.implementation_deps])
        quote_includes = depset(transitive = [target_cc.quote_includes] + [dep[CcInfo].compilation_context.quote_includes for dep in ctx.rule.attr.implementation_deps])
        system_includes = depset(transitive = [target_cc.system_includes] + [dep[CcInfo].compilation_context.system_includes for dep in ctx.rule.attr.implementation_deps])
        framework_includes = depset(transitive = [target_cc.framework_includes] + [dep[CcInfo].compilation_context.framework_includes for dep in ctx.rule.attr.implementation_deps])
        if hasattr(target_cc, "external_includes"):
            external_includes = depset(transitive = [target_cc.external_includes] + [dep[CcInfo].compilation_context.external_includes for dep in ctx.rule.attr.implementation_deps])
        else:
            external_includes = depset()
    else:
        defines = depset(transitive = [target_cc.defines, target_cc.local_defines])

        includes = target_cc.includes
        quote_includes = target_cc.quote_includes
        system_includes = target_cc.system_includes
        framework_includes = target_cc.framework_includes
        external_includes = target_cc.external_includes if hasattr(target_cc, "external_includes") else depset()

    return struct(
        includes = includes,
        quote_includes = quote_includes,
        system_includes = system_includes,
        framework_includes = framework_includes,
        external_includes = external_includes,
        defines = defines,
    )

def _create_compile_flags(target, ctx, cc_toolchain):
    feature_configuration = cc_common.configure_features(
        ctx = ctx,
        cc_toolchain = cc_toolchain,
        language = "c++",
        requested_features = ctx.features,
        unsupported_features = ctx.disabled_features,
    )

    compilation_context = _create_full_cc_compilation_context(target, ctx)

    compile_variables = cc_common.create_compile_variables(
        cc_toolchain = cc_toolchain,
        feature_configuration = feature_configuration,
        source_file = None,
        output_file = None,
        user_compile_flags = ctx.rule.attr.copts + ctx.fragments.cpp.cxxopts + ctx.fragments.cpp.copts,
        include_directories = compilation_context.includes,
        quote_include_directories = compilation_context.quote_includes,
        system_include_directories = depset(transitive = [compilation_context.system_includes, compilation_context.external_includes]),
        framework_include_directories = compilation_context.framework_includes,
        preprocessor_defines = compilation_context.defines,
    )

    compile_flags = cc_common.get_memory_inefficient_command_line(
        feature_configuration = feature_configuration,
        action_name = CPP_COMPILE_ACTION_NAME,
        variables = compile_variables,
    )
    return compile_flags

def _make_quoting_compatible_to_be_run_in_shell(command):
    # We need to copy the list to get a mutable non frozen list
    mutable_cmd = [flag for flag in command]
    for i, flag in enumerate(mutable_cmd):
        if '"' in flag:
            parts = flag.split('"')
            if len(parts) != 3:
                # We expected something following the pattern '-Dfoo="bar"'
                fail("Unexpected quoting in command flag: " + flag)
            mutable_cmd[i] = parts[0] + "'\"" + parts[1] + "\"'" + parts[2]
    return mutable_cmd

def _clang_tidy_impl(target, ctx):
    all_results = []

    cc_toolchain = find_cc_toolchain(ctx)
    compile_flags = _create_compile_flags(target, ctx, cc_toolchain)
    compile_flags = _make_quoting_compatible_to_be_run_in_shell(compile_flags)

    target_cc = target[CcInfo].compilation_context
    if hasattr(ctx.rule.attr, "implementation_deps"):
        relevant_headers = depset(transitive = [target_cc.headers] + [dep[CcInfo].compilation_context.headers for dep in ctx.rule.attr.implementation_deps])
    else:
        relevant_headers = target_cc.headers

    # clang-tidy needs to ron on compilation units, it cannot analyze header only code
    for src in ctx.rule.files.srcs:
        output = ctx.actions.declare_file("{}_clang_tidy_status".format(ctx.label.name))

        cmd = str(ctx.executable._tool_clang_tidy.path) + " " + str(src.path) + " -- "
        cmd += " ".join(compile_flags)

        # Ignore warnings about missing compilation data base
        cmd += " 2> /dev/null "

        # Pipe exit status to file since we need to generate some output for Bazel to run the action
        cmd += "; STATUS=$? ; echo ${STATUS} > " + str(output.path)

        # Fail the action if clang-tiy failed
        cmd += "; exit ${STATUS}"

        ctx.actions.run_shell(
            inputs = depset(direct = [src, ctx.executable._tool_clang_tidy, ctx.file._config], transitive = [relevant_headers, cc_toolchain.all_files]),
            command = cmd,
            mnemonic = "DwyuClangTidy",
            outputs = [output],
        )

        all_results.append(output)

    return [OutputGroupInfo(clang_tidy = all_results)]

# We are not using an upstream solution as we did not find any working as desired for us.
# At the same time, executing clang-tidy is easy enough for our use cases.
# We considered:
# - https://github.com/erenon/bazel_clang_tidy
#   + Does not support implementation_deps or external_includes
#   + Not available via BCR
#   + Original author no longer works with Bazel: https://github.com/erenon/bazel_clang_tidy/issues/35#issuecomment-1371147567
# - https://github.com/aspect-build/rules_lint
#   + Did not work for us advertized. Maybe this is just properly working when using the advertized aspect cli?
#   + Quite large with many deps, although we just need a little part. For alle the other checks we prefer pre-commit.
#
# If anybody finds this code, on the search for executing clang-tidy via Bazel, please note we do not consider this a
# good or complete implementation. This is merely something we came up with for internal usage.
clang_tidy = aspect(
    implementation = _clang_tidy_impl,
    required_providers = [CcInfo],
    fragments = ["cpp"],
    toolchains = use_cc_toolchain(mandatory = True),
    attrs = {
        "_config": attr.label(
            default = Label("//:.clang-tidy"),
            allow_single_file = True,
        ),
        "_tool_clang_tidy": attr.label(
            default = Label("@llvm_toolchain//:clang-tidy"),
            allow_files = True,
            executable = True,
            cfg = "exec",
        ),
    },
)
