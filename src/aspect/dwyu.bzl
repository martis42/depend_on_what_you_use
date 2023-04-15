load("@bazel_tools//tools/build_defs/cc:action_names.bzl", "CPP_COMPILE_ACTION_NAME")
load("@bazel_tools//tools/cpp:toolchain_utils.bzl", "find_cpp_toolchain")

def _parse_sources_impl(sources, out_files):
    for src in sources:
        file = src.files.to_list()[0]
        out_files.append(file)

def _parse_sources(attr):
    """Split source files into public and private ones"""
    public_files = []
    private_files = []

    if hasattr(attr, "srcs"):
        _parse_sources_impl(sources = attr.srcs, out_files = private_files)
    if hasattr(attr, "hdrs"):
        _parse_sources_impl(sources = attr.hdrs, out_files = public_files)
    if hasattr(attr, "textual_hdrs"):
        _parse_sources_impl(sources = attr.textual_hdrs, out_files = public_files)

    return public_files, private_files

def _do_ensure_private_deps(ctx):
    """
    The implementation_deps feature is only meaningful and available for cc_library, where in contrast to cc_binary
    and cc_test a separation between public and private files exists.
    """
    return ctx.rule.kind == "cc_library" and ctx.attr._use_implementation_deps

def _make_args(ctx, public_files, private_files, report_file, headers_info_file):
    args = ctx.actions.args()

    args.add_all("--public-files", [pf.path for pf in public_files])
    args.add_all("--private-files", [pf.path for pf in private_files])
    args.add("--headers-info", headers_info_file)
    args.add("--report", report_file)

    if ctx.attr._config.label.name != "private/dwyu_empty_config.json":
        args.add("--ignored-includes-config", ctx.file._config)

    if _do_ensure_private_deps(ctx):
        args.add("--implementation-deps-available")

    return args

def _get_include_paths(label, system_includes, header_file):
    """
    Get all paths at which a header file is available to code using it.

    Args:
        label: Label of the target providing the header file
        system_includes: system_include paths of the target providing the header file
        header_file: Header file
    """

    # Paths at which headers are available from targets which utilize "include_prefix" or "strip_include_prefix"
    if "_virtual_includes" in header_file.path:
        return [header_file.path.partition("_virtual_includes" + "/" + label.name + "/")[2]]

    # Paths at which headers are available from targets which utilize "includes = [...]"
    includes = []
    for si in system_includes.to_list():
        si_path = si + "/"
        if header_file.path.startswith(si_path):
            includes.append(header_file.path.partition(si_path)[2])
    if includes:
        return includes

    # Paths for headers from external repos are prefixed with the external repo root. But the headers are
    # included relative to the external workspace root.
    if header_file.owner.workspace_root != "":
        return [header_file.path.replace(header_file.owner.workspace_root + "/", "")]

    # Default case for single header in workspace target without any special attributes
    return [header_file.short_path]

def _extract_header_files(target, is_target_under_inspection):
    """
    The file location of the headers is used by DWYU to resolve relative include statements.
    We support only relative includes to files from the own workspace. Thus, we ignore header files from external
    workspaces.
    """
    header_files = []
    if not target.label.workspace_root.startswith("external"):
        header_files.extend([hdr.short_path for hdr in target[CcInfo].compilation_context.direct_public_headers])
        header_files.extend([hdr.short_path for hdr in target[CcInfo].compilation_context.direct_textual_headers])
        if is_target_under_inspection:
            header_files.extend([hdr.short_path for hdr in target[CcInfo].compilation_context.direct_private_headers])
    return header_files

def _make_target_info(target):
    include_paths = []
    for hdr in target[CcInfo].compilation_context.direct_headers:
        inc = _get_include_paths(
            label = target.label,
            system_includes = target[CcInfo].compilation_context.system_includes,
            header_file = hdr,
        )
        include_paths.extend(inc)

    return struct(
        target = str(target.label),
        include_paths = include_paths,
        header_files = _extract_header_files(target = target, is_target_under_inspection = True),
    )

def _make_dep_info(dep):
    include_paths = []
    for hdr in dep[CcInfo].compilation_context.direct_public_headers:
        inc = _get_include_paths(
            label = dep.label,
            system_includes = dep[CcInfo].compilation_context.system_includes,
            header_file = hdr,
        )
        include_paths.extend(inc)

    for hdr in dep[CcInfo].compilation_context.direct_textual_headers:
        inc = _get_include_paths(
            label = dep.label,
            system_includes = dep[CcInfo].compilation_context.system_includes,
            header_file = hdr,
        )
        include_paths.extend(inc)

    return struct(
        target = str(dep.label),
        include_paths = include_paths,
        header_files = _extract_header_files(target = dep, is_target_under_inspection = False),
    )

def _make_headers_info(target, public_deps, private_deps, defines):
    """
    Create a struct summarizing all information about the target and the dependencies required for executing the
    DWYU logic.

    Args:
        target: Current target under inspection
        public_deps: Direct public dependencies of target under inspection
        private_deps: Direct private dependencies of target under inspection
        defines: Defines relevant for the preprocessor
    """
    return struct(
        self = _make_target_info(target),
        public_deps = [_make_dep_info(dep) for dep in public_deps],
        private_deps = [_make_dep_info(dep) for dep in private_deps],
        defines = defines,
    )

def _label_to_name(label):
    return str(label).replace("@", "").replace("//", "").replace("/", "_").replace(":", "_")

def extract_defines_from_compiler_flags(compiler_flags):
    """
    We extract the relevant defines from the compiler command line flags. We utilize the compiler flags since the
    toolchain can set defines which are not available through CcInfo or the cpp fragments. Furthermore, defines
    potentially overwrite or deactivate each other depending on the order in which they appear in the compiler
    command. Thus, this is the only way to make sure DWYU analyzes what would actually happen during compilation.

    Args:
        compiler_flags: List of flags making up the compilation command
    Returns:
        List of defines
    """
    defines = {}

    for cflag in compiler_flags:
        if cflag.startswith("-U"):
            undefine = cflag[2:]
            undefine_name = undefine.split("=", 1)[0]
            if undefine_name in defines.keys():
                defines.pop(undefine_name)
        if cflag.startswith("-D"):
            define = cflag[2:]
            define_name = define.split("=", 1)[0]
            defines[define_name] = define

    return defines.values()

def _gather_defines(ctx, target_compilation_context):
    cc_toolchain = find_cpp_toolchain(ctx)

    feature_configuration = cc_common.configure_features(
        ctx = ctx,
        cc_toolchain = cc_toolchain,
        requested_features = ctx.features,
        unsupported_features = ctx.disabled_features,
    )
    compile_variables = cc_common.create_compile_variables(
        feature_configuration = feature_configuration,
        cc_toolchain = cc_toolchain,
        user_compile_flags = ctx.rule.attr.copts + ctx.fragments.cpp.cxxopts + ctx.fragments.cpp.copts,
        preprocessor_defines = depset(transitive = [
            target_compilation_context.defines,
            target_compilation_context.local_defines,
        ]),
    )

    # We cannot directly work with 'compile_variables' in Starlark, thus we translate them into string representation
    compiler_command_line_flags = cc_common.get_memory_inefficient_command_line(
        feature_configuration = feature_configuration,
        action_name = CPP_COMPILE_ACTION_NAME,
        variables = compile_variables,
    )

    return extract_defines_from_compiler_flags(compiler_command_line_flags)

def dwyu_aspect_impl(target, ctx):
    """
    Implementation for the "Depend on What You Use" (DWYU) aspect.

    Args:
        target: Target under inspection. Aspect will only do work for specific cc_* rules
        ctx: Context

    Returns:
        OutputGroup containing the generated report file
    """
    if not ctx.rule.kind in ["cc_binary", "cc_library", "cc_test"]:
        return []

    # Skip incompatible targets
    # Ideally we should check for the existence of "IncompatiblePlatformProvider".
    # However, this provider is not available in Starlark
    if not CcInfo in target:
        return []

    public_files, private_files = _parse_sources(ctx.rule.attr)
    if not public_files and not private_files:
        return []

    public_deps = ctx.rule.attr.deps
    private_deps = ctx.rule.attr.implementation_deps if hasattr(ctx.rule.attr, "implementation_deps") else []
    defines = _gather_defines(ctx, target[CcInfo].compilation_context)

    target_name = _label_to_name(target.label)
    report_file = ctx.actions.declare_file("{}_dwyu_report.json".format(target_name))
    headers_info_file = ctx.actions.declare_file("{}_headers_info.json".format(target_name))
    headers_info = _make_headers_info(target = target, public_deps = public_deps, private_deps = private_deps, defines = defines)
    ctx.actions.write(headers_info_file, json.encode_indent(headers_info))

    args = _make_args(
        ctx = ctx,
        public_files = public_files,
        private_files = private_files,
        report_file = report_file,
        headers_info_file = headers_info_file,
    )
    ctx.actions.run(
        executable = ctx.executable._dwyu_binary,
        inputs = [headers_info_file, ctx.file._config] + public_files + private_files,
        outputs = [report_file],
        mnemonic = "CompareIncludesToDependencies",
        progress_message = "Analyze dependencies of {}".format(target.label),
        arguments = [args],
    )

    if ctx.attr._recursive:
        transitive_reports = [dep[OutputGroupInfo].cc_dwyu_output for dep in ctx.rule.attr.deps]
    else:
        transitive_reports = []
    accumulated_reports = depset(direct = [report_file], transitive = transitive_reports)

    return [OutputGroupInfo(cc_dwyu_output = accumulated_reports)]
