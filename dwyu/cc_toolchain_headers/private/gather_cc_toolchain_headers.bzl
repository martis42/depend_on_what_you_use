load("@rules_cc//cc:action_names.bzl", "CPP_COMPILE_ACTION_NAME")
load("@rules_cc//cc:find_cc_toolchain.bzl", "find_cc_toolchain", "use_cc_toolchain")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("//dwyu/cc_toolchain_headers:providers.bzl", "DwyuCcToolchainHeadersInfo")
load("//dwyu/private:utils.bzl", "make_param_file_args")

visibility("//dwyu/cc_toolchain_headers/...")

def _make_verbose(ctx, args):
    if "DWYU_VERBOSE" in ctx.configuration.default_shell_env:
        args.add("--verbose")

def _get_minimal_compile_action(ctx, cc_toolchain):
    feature_configuration = cc_common.configure_features(ctx = ctx, cc_toolchain = cc_toolchain, language = "c++")
    compile_variables = cc_common.create_compile_variables(cc_toolchain = cc_toolchain, feature_configuration = feature_configuration, source_file = ctx.file._empty_cpp.path)

    compile_env = cc_common.get_environment_variables(feature_configuration = feature_configuration, action_name = CPP_COMPILE_ACTION_NAME, variables = compile_variables)
    compile_cmd = cc_common.get_memory_inefficient_command_line(feature_configuration = feature_configuration, action_name = CPP_COMPILE_ACTION_NAME, variables = compile_variables)

    return compile_cmd, compile_env

def extract_msvc_include_paths(ctx, env, cmd):
    include_paths = []

    if "INCLUDE" in env:
        include_var = env["INCLUDE"]
        for ip in include_var.split(ctx.configuration.host_path_separator):
            if ip not in include_paths:
                include_paths.append(ip)

    for i in range(len(cmd) - 1):
        if cmd[i] == "/I" and cmd[i + 1] not in include_paths:
            include_paths.append(cmd[i + 1])

    return include_paths

def _get_headers_for_gcc_like_toolchain(ctx, cc_toolchain, output):
    """
    CcToolchainInfo.built_in_include_directories is an optional field. Nothing enforces this being set at all or being set correctly.
    Furthermore, multiple things can influence the include paths pointing to the toolchain headers:
    - environment variables
    - paths hard coded into the compiler
    - a sysroot
    - compiler arguments point to include paths which are unconditionally added to all compile actions

    For compilers following the gcc/clang CLI and output format, the most resilient way to gather all relevant include directories is to use the compiler in verbose mode.
    It will then print in an easily parsable way all include paths used by the compiler. To do this, we create a minimal compile command based on an empty input file.
    We execute this minimal compile command in verbose mode and analyze the output to get all relevant include directories.
    """
    compile_cmd, compile_env = _get_minimal_compile_action(ctx, cc_toolchain)
    full_cmd = [
        # Explicitly request processing C++
        "-x",
        "c++",
        # Only preprocess to not waste resources
        "-E",
        # Use verbose mode to see include directories available to compiler in stderr
        "-v",
    ] + compile_cmd

    stdout = ctx.actions.declare_file("{}_gcc_like_stdout".format(ctx.label.name))
    stderr = ctx.actions.declare_file("{}_gcc_like_stderr".format(ctx.label.name))

    # Even if we don't utilize the stdout capture, we capture it to not clutter the output without proper context to understand the displayed lines
    cmd = "{COMPILER} {ARGS} > {STDOUT} 2> {STDERR}".format(COMPILER = cc_toolchain.compiler_executable, ARGS = " ".join(full_cmd), STDOUT = stdout.path, STDERR = stderr.path)
    ctx.actions.run_shell(
        inputs = depset(direct = [ctx.file._empty_cpp], transitive = [cc_toolchain.all_files]),
        outputs = [stdout, stderr],
        command = cmd,
        mnemonic = "DwyuQueryGccLikeCompilerIncludeDirs",
        env = compile_env,
    )

    args = make_param_file_args(ctx)
    args.add("--gcc_like_include_paths_info", stderr)
    args.add("--output", output)
    _make_verbose(ctx, args)
    ctx.actions.run(
        executable = ctx.executable._gatherer,
        inputs = depset(direct = [stderr], transitive = [cc_toolchain.all_files]),
        outputs = [output],
        mnemonic = "DWYUGatherGccLikeToolchainHeaders",
        arguments = [args],
    )

def _get_headers_for_msvc_like_toolchain(ctx, cc_toolchain, output):
    """
    MSVC does not offer a way to report all used include directories. It can report all included files, but this does
    not tell you relative to which path those can ce included.
    MSVC listens to the environment variable 'INCLUDE' to know at which paths to look for header files. Furthermore,
    a CC toolchain can add command line args to each compilation command to point to toolchain directories not
    included in the 'INCLUDE' variable.
    Thus, we create a minimal compilation command and its corresponding environment variables to find all header
    files associated with the CC toolchain.
    """
    compile_cmd, compile_env = _get_minimal_compile_action(ctx, cc_toolchain)

    include_paths = extract_msvc_include_paths(ctx, compile_env, compile_cmd)

    args = make_param_file_args(ctx)
    args.add_all("--include_directories", include_paths, omit_if_empty = False)
    args.add("--output", output)
    _make_verbose(ctx, args)
    ctx.actions.run(
        executable = ctx.executable._gatherer,
        inputs = cc_toolchain.all_files,
        outputs = [output],
        mnemonic = "DWYUGatherMsvcLikeToolchainHeaders",
        arguments = [args],
    )

def _get_headers_without_compiler_knowledge(ctx, cc_toolchain, output):
    """
    We don't know the compiler and thus do not know the proper strategy to find all include paths available to it.
    If the CC toolchain is properly defined, all relevant include paths for toolchain headers should be listed in CcToolchainInfo.built_in_include_directories.
    This is however an optional field without any sanity checks done by Bazel. Thus, using this is a best guess without any guarantee of knowing all relevant include paths.
    """

    # buildifier: disable=print
    print(
        "WARNING: DWYU is using a fallback logic for compiler '{compiler}' to find your CC toolchain headers.".format(compiler = cc_toolchain.compiler) +
        " This is a best effort without any guarantees. Please have a look at the documentation for the DWYU aspect attribute 'ignore_cc_toolchain_headers' for more information.",
    )

    args = make_param_file_args(ctx)
    args.add_all("--include_directories", cc_toolchain.built_in_include_directories)
    args.add("--output", output)
    _make_verbose(ctx, args)
    ctx.actions.run(
        executable = ctx.executable._gatherer,
        inputs = cc_toolchain.all_files,
        outputs = [output],
        mnemonic = "DWYUGatherUnknownCompilerToolchainHeaders",
        arguments = [args],
    )

def _gather_toolchain_headers_impl(ctx):
    cc_toolchain = find_cc_toolchain(ctx)
    output = ctx.actions.declare_file("{}_toolchain_headers_info.json".format(ctx.label.name))

    if "gcc" in cc_toolchain.compiler or "clang" in cc_toolchain.compiler:
        _get_headers_for_gcc_like_toolchain(ctx, cc_toolchain, output)
        return [
            DwyuCcToolchainHeadersInfo(headers_info = output),
            DefaultInfo(files = depset(direct = [output])),
        ]
    if "msvc" in cc_toolchain.compiler:
        _get_headers_for_msvc_like_toolchain(ctx, cc_toolchain, output)
        return [
            DwyuCcToolchainHeadersInfo(headers_info = output),
            DefaultInfo(files = depset(direct = [output])),
        ]
    if cc_toolchain.built_in_include_directories:
        _get_headers_without_compiler_knowledge(ctx, cc_toolchain, output)
        return [
            DwyuCcToolchainHeadersInfo(headers_info = output),
            DefaultInfo(files = depset(direct = [output])),
        ]

    fail("DWYU does not understand your CC toolchain. Compiler '{compiler}' is not supported and `CcToolchainInfo.built_in_include_directories` is not set.".format(compiler = cc_toolchain.compiler) +
         " Please have a look at the documentation for the DWYU aspect attribute 'ignore_cc_toolchain_headers' for more information.")

doc = """
Analyze the active CC toolchain and extract possible include statements to header files which are available through the CC toolchain without any explicit dependency to a Bazel target.
Typically those are the standard library and system headers.
There is no reliable API available in Starlark to get this information for all possible CC toolchains, since [CcToolchainInfo.built_in_include_directories](https://bazel.build/rules/lib/providers/CcToolchainInfo#built_in_include_directories) is an optional field without sanity checking.
Thus, the implementation of this rule uses knowledge about the most common compilers.
It might not work as expected for compilers besides GCC, Clang and MSVC.
"""

gather_cc_toolchain_headers = rule(
    implementation = _gather_toolchain_headers_impl,
    toolchains = use_cc_toolchain(mandatory = True),
    fragments = ["cpp"],
    provides = [DwyuCcToolchainHeadersInfo],
    doc = doc,
    attrs = {
        # Remove after minimum Bazel version is 7, see https://docs.google.com/document/d/14vxMd3rTpzAwUI9ng1km1mp-7MrVeyGFnNbXKF_XhAM/edit?tab=t.0
        "_cc_toolchain": attr.label(default = Label("@rules_cc//cc:current_cc_toolchain")),
        "_empty_cpp": attr.label(
            default = Label("//dwyu/cc_toolchain_headers/private:empty.cpp"),
            allow_single_file = True,
        ),
        "_gatherer": attr.label(
            default = Label("//dwyu/cc_toolchain_headers/private:gather_cc_toolchain_headers_tool"),
            executable = True,
            cfg = "exec",
        ),
    },
)
