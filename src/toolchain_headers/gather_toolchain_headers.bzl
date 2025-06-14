load("@bazel_tools//tools/build_defs/cc:action_names.bzl", "CPP_COMPILE_ACTION_NAME")
load("@bazel_tools//tools/cpp:toolchain_utils.bzl", "find_cpp_toolchain")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load(":providers.bzl", "DwyuCcToolchainHeadersInfo")

# TODO move code into private section with limited visibility, so the symbols here can be public

def extract_include_paths(cmd, compiler):
    """
    Given a compilation command extract all include search paths which were provided via the command.

    Args:
        cmd: Compilation command which is searched for include paths
        compiler: For which compiler is the command used.
                  Tells us for which flags we have to look to identify include paths.
                  The possible values are typically the names of these config settings https://github.com/bazelbuild/rules_cc/blob/main/cc/compiler/BUILD.

    Returns:
        List of unique include paths
    """
    if compiler in ["clang", "clang-cl", "emscripten", "gcc", "mingw-gcc"]:
        include_keys = ["-isystem", "-iquote", "-I"]
    elif compiler == "msvc-cl":
        include_keys = ["/I"]
    else:
        fail("Unknown compiler, cannot parse command line")

    include_paths = []
    for i in range(len(cmd) - 1):
        if cmd[i] in include_keys and cmd[i + 1] not in include_paths:
            include_paths.append(cmd[i + 1])

    return include_paths

def _create_minimal_compile_cmd(ctx, cc_toolchain):
    """We cannot directly work with 'compile_variables' in Starlark, thus we translate them into a string representation"""
    feature_configuration = cc_common.configure_features(ctx = ctx, cc_toolchain = cc_toolchain, language = "c++")
    compile_variables = cc_common.create_compile_variables(cc_toolchain = cc_toolchain, feature_configuration = feature_configuration)
    return cc_common.get_memory_inefficient_command_line(feature_configuration = feature_configuration, action_name = CPP_COMPILE_ACTION_NAME, variables = compile_variables)

def _get_toolchain_system_includes(ctx, cc_toolchain):
    """
    The CC toolchain tells us about all hermetically provided files and and all include paths to system dirs. However,
    it does not provide us with the list of include paths relative to which the hermetically provided toolchain headers
    can be discovered. To obtain this information, we construct a minimal compilation command without providing any
    custom include paths. The include paths which are unconditionally added to the compilation command are those
    pointing to the hermetically provided header files.
    """
    compile_cmd = _create_minimal_compile_cmd(ctx, cc_toolchain)
    return extract_include_paths(compile_cmd, cc_toolchain.compiler)

def _gather_toolchain_headers_impl(ctx):
    cc_toolchain = find_cpp_toolchain(ctx)

    toolchain_include_directories = _get_toolchain_system_includes(ctx, cc_toolchain)

    output = ctx.actions.declare_file("{}_toolchain_headers_info.json".format(ctx.label.name))
    args = ctx.actions.args()
    args.use_param_file("--param_file=%s")
    args.add_all("--built_in_include_directories", cc_toolchain.built_in_include_directories, omit_if_empty = False)
    args.add_all("--toolchain_files", cc_toolchain.all_files, omit_if_empty = False, expand_directories = True)
    args.add_all("--toolchain_include_directories", toolchain_include_directories, omit_if_empty = False)
    args.add("--output", output)
    ctx.actions.run(
        executable = ctx.executable._gatherer,
        inputs = cc_toolchain.all_files,
        outputs = [output],
        mnemonic = "DWYUGatherToolchainHeaders",
        arguments = [args],
    )

    return [
        DwyuCcToolchainHeadersInfo(headers_info = output),
        DefaultInfo(files = depset(direct = [output])),
    ]

# TODO documentation
# TODO allow custom mapping of compiler to include path flags (mention only possible to add multiple dirs by repeating the flag)
gather_toolchain_headers = rule(
    implementation = _gather_toolchain_headers_impl,
    toolchains = ["@bazel_tools//tools/cpp:toolchain_type"],
    fragments = ["cpp"],
    provides = [DwyuCcToolchainHeadersInfo],
    doc = "TBD",
    attrs = {
        # Remove this legacy pattern after minimum Bazel version is 7, see https://docs.google.com/document/d/14vxMd3rTpzAwUI9ng1km1mp-7MrVeyGFnNbXKF_XhAM/edit?tab=t.0
        "_cc_toolchain": attr.label(
            default = Label("@bazel_tools//tools/cpp:current_cc_toolchain"),
        ),
        "_gatherer": attr.label(
            default = Label("@depend_on_what_you_use//src/toolchain_headers:gather_toolchain_headers"),
            executable = True,
            cfg = "exec",
            doc = "Search all header files discoverable through the active C/C++ toolchain and store their paths in a file",
        ),
    },
)
