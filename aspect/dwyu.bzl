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

def _make_args(ctx, target, public_files, private_files, report_file, headers_info_file, ensure_private_deps):
    args = ctx.actions.args()

    args.add_all("--public-files", [pf.path for pf in public_files])
    args.add_all("--private-files", [pf.path for pf in private_files])
    args.add("--headers-info", headers_info_file)
    args.add("--target", target)
    args.add("--report", report_file)

    if ctx.attr._config.label.name != "private/dwyu_empty_config.json":
        args.add("--config", ctx.file._config)

    if ensure_private_deps:
        args.add("--implementation-deps-available")

    if ctx.attr._min_utilization > 0:
        args.add("--min-dependency-utilization", ctx.attr._min_utilization)

    return args

def _get_available_include_paths(label, system_includes, header_file):
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
    # included relative to the external workspace rootbs users
    if header_file.owner.workspace_root != "":
        return [header_file.path.replace(header_file.owner.workspace_root + "/", "")]

    # Default case for single header in workspace target without any special attributes
    return [header_file.short_path]

def _make_target_info(target):
    includes = []
    for hdr in target[CcInfo].compilation_context.direct_headers:
        inc = _get_available_include_paths(
            label = target.label,
            system_includes = target[CcInfo].compilation_context.system_includes,
            header_file = hdr,
        )
        includes.extend(inc)

    return struct(target = str(target.label), headers = [inc for inc in includes])

def _make_dep_info(dep):
    includes = []
    for hdr in dep[CcInfo].compilation_context.direct_public_headers:
        inc = _get_available_include_paths(
            label = dep.label,
            system_includes = dep[CcInfo].compilation_context.system_includes,
            header_file = hdr,
        )
        includes.extend(inc)

    for hdr in dep[CcInfo].compilation_context.direct_textual_headers:
        inc = _get_available_include_paths(
            label = dep.label,
            system_includes = dep[CcInfo].compilation_context.system_includes,
            header_file = hdr,
        )
        includes.extend(inc)

    return struct(target = str(dep.label), headers = [inc for inc in includes])

def _make_headers_info(target, deps, impl_deps):
    """
    Create a struct summarizing all information about the target and the dependency headers required for DWYU.

    Args:
        target: Current target under inspection
        deps: Direct dependencies of target under inspection
        impl_deps: Implementation dependencies of target under inspection
    """
    return struct(
        self = _make_target_info(target),
        public_deps = [_make_dep_info(dep) for dep in deps],
        private_deps = [_make_dep_info(dep) for dep in impl_deps],
    )

def _label_to_name(label):
    return str(label).replace("//", "").replace("/", "_").replace(":", "_")

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

    implementation_deps = []
    ensure_private_deps = False
    if ctx.attr._use_implementation_deps and hasattr(ctx.rule.attr, "implementation_deps"):
        implementation_deps = ctx.rule.attr.implementation_deps
        ensure_private_deps = True

    public_files, private_files = _parse_sources(ctx.rule.attr)
    report_file = ctx.actions.declare_file("{}_report.txt".format(_label_to_name(target.label)))
    headers_info_file = ctx.actions.declare_file("{}_deps_info.json".format(_label_to_name(target.label)))
    headers_info = _make_headers_info(target = target, deps = ctx.rule.attr.deps, impl_deps = implementation_deps)
    ctx.actions.write(headers_info_file, json.encode_indent(headers_info))

    args = _make_args(
        ctx = ctx,
        target = target.label,
        public_files = public_files,
        private_files = private_files,
        report_file = report_file,
        headers_info_file = headers_info_file,
        ensure_private_deps = ensure_private_deps,
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
