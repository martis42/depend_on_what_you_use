load("@rules_cc//cc:action_names.bzl", "CPP_COMPILE_ACTION_NAME")
load("@rules_cc//cc:find_cc_toolchain.bzl", "find_cc_toolchain", "use_cc_toolchain")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("//src/toolchain_headers:providers.bzl", "DwyuCcToolchainHeadersInfo")
load("//src/utils:utils.bzl", "print_cc_toolchain")

# We compare the compiler name via substring matching to the compiler specified by the toolchain.
# Structure: {<compiler_name>: [<options_for_specifying_include_paths>]}
_COMPILER_OPTIONS_MAP = {
    "clang": ["-isystem", "-iquote", "-I"],
    "gcc": ["-isystem", "-iquote", "-I"],
    "msvc": ["/I"],
}

def extract_include_paths(cmd, compiler):
    """
    Given a compilation command extract all include search paths which were provided via the command.

    Args:
        cmd: Compilation command which is searched for include paths
        compiler: For which compiler the command was generated

    Returns:
        List of unique include paths
    """
    include_options = None
    for compiler_name, options in _COMPILER_OPTIONS_MAP.items():
        if compiler_name in compiler:
            include_options = options
            break
    if include_options == None:
        fail("Unknown compiler '{}'. Cannot parse compile command '{}'".format(compiler, cmd))

    include_paths = []
    for i in range(len(cmd) - 1):
        if cmd[i] in include_options and cmd[i + 1] not in include_paths:
            include_paths.append(cmd[i + 1])

    return include_paths

def _create_minimal_compile_cmd(ctx, cc_toolchain):
    feature_configuration = cc_common.configure_features(ctx = ctx, cc_toolchain = cc_toolchain, language = "c++")
    compile_variables = cc_common.create_compile_variables(cc_toolchain = cc_toolchain, feature_configuration = feature_configuration)

    env = cc_common.get_environment_variables(
        feature_configuration = feature_configuration,
        action_name = CPP_COMPILE_ACTION_NAME,
        variables = compile_variables,
    )

    # buildifier: disable=print
    print("COMPILE ENV", len(env))
    for var, value in env.items():
        # buildifier: disable=print
        print("{} : {}".format(var, value))

    # We cannot properly distinguish between C and C++ here. Either way, the C++ command should also work for C projects
    # with respect to what we want to achieve, as long as the active toolchain did not choose to implement solely C actions.
    return cc_common.get_memory_inefficient_command_line(feature_configuration = feature_configuration, action_name = CPP_COMPILE_ACTION_NAME, variables = compile_variables)

def _get_command_line_includes(ctx, cc_toolchain):
    """
    'CcToolchainInfo.built_in_include_directories' is not providing all possible include paths to toolchain files. The
    CC toolchain implementation can also provide include paths via the command line. For example when the toolchain
    makes hermetically provided files available, which are not structured in a way that a sysroot change approach works.
    Or those are files on top of the standard library system headers. Or the toolchain compiler does not support
    specifying a sysroot.
    To get the information of include paths provided via the command line we construct a minimal compilation command
    without providing any custom include paths. The include paths which are unconditionally added to the compilation
    command are those include paths pointing to toolchain files which we are looking for.

    For now this ignores the possibility to use '--sysroot' to point to system and standard library headers. The
    documentation for cc_common function 'create_cc_toolchain_config_info' [0] attribute 'cxx_builtin_include_directories'
    suggests the sysroot should be incorporated into the builtin directories, which we already process. Thus, we are able
    to process CC toolchains providing paths to sysroot locations following the documented best practice. However, this
    best practice is not enforced. It seems providing valid built in directories to CcToolchainInfo is overall optional.
    For now we ignore cases where 'built_in_include_directories' is not correct. If such cases exist in common toolchains,
    we will investigate handling this case at later point in time.

    [0]: https://bazel.build/rules/lib/toplevel/cc_common#create_cc_toolchain_config_info
    """
    compile_cmd = _create_minimal_compile_cmd(ctx, cc_toolchain)

    # buildifier: disable=print
    print("COMPILE_CMD ", compile_cmd)

    return extract_include_paths(compile_cmd, cc_toolchain.compiler)

def _gather_toolchain_headers_impl(ctx):
    cc_toolchain = find_cc_toolchain(ctx)

    print_cc_toolchain(cc_toolchain)

    # buildifier: disable=print
    print("SHELL ENV ", ctx.configuration.default_shell_env)

    # Relevant include paths on top of 'CcToolchainInfo.built_in_include_directories'
    toolchain_include_directories = _get_command_line_includes(ctx, cc_toolchain)

    output = ctx.actions.declare_file("{}_toolchain_headers_info.json".format(ctx.label.name))
    args = ctx.actions.args()
    args.use_param_file("--param_file=%s")
    args.add_all("--built_in_include_directories", cc_toolchain.built_in_include_directories, omit_if_empty = False)  # Those are not part of the command line
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

doc = """
Analyze the active CC toolchain and extract include paths to header files which are available through the CC toolchain without any explicit dependency to a Bazel target.
Typically those are the standard library and system headers.

This rule analyzes [`CcToolchainInfo.built_in_include_directories`](https://bazel.build/rules/lib/providers/CcToolchainInfo#built_in_include_directories) and the toolchain compiler command line arguments to obtain this information.
We assume that all paths, which are not passed via the compiler command line with flags like `-isystem`, are specified via `CcToolchainInfo.built_in_include_directories`.
This includes also providing custom sysroots, which should be incorporated into `CcToolchainInfo.built_in_include_directories` according to the documentation of cc_common function [create_cc_toolchain_config_info](https://bazel.build/rules/lib/toplevel/cc_common#create_cc_toolchain_config_info).
"""

gather_toolchain_headers = rule(
    implementation = _gather_toolchain_headers_impl,
    toolchains = use_cc_toolchain(mandatory = True),
    fragments = ["cpp"],
    provides = [DwyuCcToolchainHeadersInfo],
    doc = doc,
    attrs = {
        # Remove CC_TOOLCHAIN_ATTRS after minimum Bazel version is 7, see https://docs.google.com/document/d/14vxMd3rTpzAwUI9ng1km1mp-7MrVeyGFnNbXKF_XhAM/edit?tab=t.0
        "_cc_toolchain": attr.label(default = Label("@rules_cc//cc:current_cc_toolchain")),
        "_gatherer": attr.label(
            default = Label("@depend_on_what_you_use//src/toolchain_headers/private:gather_toolchain_headers"),
            executable = True,
            cfg = "exec",
        ),
    },
)
