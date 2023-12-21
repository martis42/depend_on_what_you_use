load("@bazel_tools//tools/build_defs/cc:action_names.bzl", "CPP_COMPILE_ACTION_NAME")
load("@bazel_tools//tools/cpp:toolchain_utils.bzl", "find_cpp_toolchain")
load("@depend_on_what_you_use//src/cc_info_mapping:cc_info_mapping.bzl", "DwyuCcInfoRemappingsInfo")
load("@rules_cc//cc:defs.bzl", "CcInfo", "cc_common")

def _get_target_sources(rule):
    public_files = []
    private_files = []

    if hasattr(rule.attr, "srcs"):
        private_files.extend(rule.files.srcs)
    if hasattr(rule.attr, "hdrs"):
        public_files.extend(rule.files.hdrs)
    if hasattr(rule.attr, "textual_hdrs"):
        public_files.extend(rule.files.textual_hdrs)

    return public_files, private_files

def _get_relevant_header(target_context, is_target_under_inspection):
    if is_target_under_inspection:
        return target_context.direct_public_headers + target_context.direct_private_headers + target_context.direct_textual_headers
    else:
        return target_context.direct_public_headers + target_context.direct_textual_headers

def _process_target(ctx, target, defines, output_path, is_target_under_inspection, verbose):
    processing_output = ctx.actions.declare_file(output_path)
    cc_context = target.cc_info.compilation_context
    header_files = _get_relevant_header(
        target_context = cc_context,
        is_target_under_inspection = is_target_under_inspection,
    )

    args = ctx.actions.args()
    args.add("--target", str(target.label))
    args.add("--output", processing_output)
    args.add_all("--header_files", header_files, expand_directories = True, omit_if_empty = False)
    if is_target_under_inspection:
        args.add_all("--includes", cc_context.includes, omit_if_empty = False)
        args.add_all("--quote_includes", cc_context.quote_includes, omit_if_empty = False)
        args.add_all("--system_includes", cc_context.system_includes, omit_if_empty = False)
        args.add_all("--defines", defines)
    if verbose:
        args.add("--verbose")

    ctx.actions.run(
        inputs = header_files,
        executable = ctx.executable._process_target,
        arguments = [args],
        outputs = [processing_output],
    )

    return processing_output

def _process_dependencies(ctx, target, deps, verbose):
    return [_process_target(
        ctx,
        target = dep,
        defines = [],
        output_path = "{}_processed_dep_{}.json".format(target.label.name, hash(str(dep.label))),
        is_target_under_inspection = False,
        verbose = verbose,
    ) for dep in deps]

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

def _exchange_cc_info(deps, mapping):
    transformed = []
    mapping_info = mapping[0][DwyuCcInfoRemappingsInfo].mapping
    for dep in deps:
        if dep.label in mapping_info:
            transformed.append(struct(label = dep.label, cc_info = mapping_info[dep.label]))
        else:
            transformed.append(struct(label = dep.label, cc_info = dep[CcInfo]))
    return transformed

def _preprocess_deps(ctx):
    """
    Normally this function does nothing and simply stores dependencies and their CcInfo providers in a specific format.
    If the user chooses to use the target mapping feature, we exchange here the CcInf provider for some targets with a
    different one.
    """
    target_impl_deps = []
    if ctx.attr._target_mapping:
        target_deps = _exchange_cc_info(deps = ctx.rule.attr.deps, mapping = ctx.attr._target_mapping)
        if hasattr(ctx.rule.attr, "implementation_deps"):
            pass
    else:
        target_deps = [struct(label = dep.label, cc_info = dep[CcInfo]) for dep in ctx.rule.attr.deps]
        if hasattr(ctx.rule.attr, "implementation_deps"):
            target_impl_deps = [struct(label = dep.label, cc_info = dep[CcInfo]) for dep in ctx.rule.attr.implementation_deps]

    return target_deps, target_impl_deps

def _do_ensure_private_deps(ctx):
    """
    The implementation_deps feature is only meaningful and available for cc_library, where in contrast to cc_binary
    and cc_test a separation between public and private files exists.
    """
    return ctx.rule.kind == "cc_library" and ctx.attr._use_implementation_deps

def _gather_transitive_reports(ctx):
    """
    In recursive operation mode we have to propagate the DWYU report files of all transitive dependencies to ensure
    the DWYU actions run for all targets. Not doing this will cause DWYU not being executed at all as without returning
    the report files Bazel prunes the DWYU actions.
    """
    reports = []
    if ctx.attr._recursive:
        reports.extend([dep[OutputGroupInfo].cc_dwyu_output for dep in ctx.rule.attr.deps])
        if hasattr(ctx.rule.attr, "implementation_deps"):
            reports.extend([dep[OutputGroupInfo].cc_dwyu_output for dep in ctx.rule.attr.implementation_deps])
    return reports

def dwyu_aspect_impl(target, ctx):
    """
    Implementation for the "Depend on What You Use" (DWYU) aspect.

    Args:
        target: Target under inspection. Aspect will only do work for specific cc_* rules
        ctx: Context

    Returns:
        OutputGroup containing the generated report file
    """

    # Remove when minimum Bazel version is 7.0.0, see https://github.com/bazelbuild/bazel/issues/19609
    # DWYU is only able to work on targets providing CcInfo. Other targets shall be skipped.
    if not CcInfo in target:
        return []

    # While we limit ourselves right now in the early project phase, we aim at supporting all cc_ like rules accepting
    # 'hdrs' and 'srcs' attributes and providing CcInfo
    if not ctx.rule.kind in ["cc_binary", "cc_library", "cc_test"]:
        return []

    # Skip targets which explicitly opt-out
    if any([tag in ctx.attr._skipped_tags for tag in ctx.rule.attr.tags]):
        return []

    public_files, private_files = _get_target_sources(ctx.rule)

    # We skip targets which have no source files. cc_* targets can also be of value if they only specify the 'deps'
    # attribute without own sources. But those targets are not of interest for DWYU.
    if not public_files and not private_files:
        return []

    processed_target = _process_target(
        ctx,
        target = struct(label = target.label, cc_info = target[CcInfo]),
        defines = _gather_defines(ctx, target_compilation_context = target[CcInfo].compilation_context),
        output_path = "{}_processed_target_under_inspection.json".format(target.label.name),
        is_target_under_inspection = True,
        verbose = False,
    )

    target_deps, target_impl_deps = _preprocess_deps(ctx)

    # TODO Investigate if we can prevent running this multiple times for the same dep if multiple
    #      target_under_inspection have the same dependency
    processed_deps = _process_dependencies(ctx, target = target, deps = target_deps, verbose = False)
    processed_impl_deps = _process_dependencies(ctx, target = target, deps = target_impl_deps, verbose = False)

    report_file = ctx.actions.declare_file("{}_dwyu_report.json".format(target.label.name))
    args = ctx.actions.args()
    args.add("--report", report_file)
    args.add_all("--public_files", public_files, expand_directories = True, omit_if_empty = False)
    args.add_all("--private_files", private_files, expand_directories = True, omit_if_empty = False)
    args.add("--target_under_inspection", processed_target)
    args.add_all("--deps", processed_deps, omit_if_empty = False)
    args.add_all("--implementation_deps", processed_impl_deps, omit_if_empty = False)
    if ctx.attr._config:
        args.add("--ignored_includes_config", ctx.files._config[0])
    if _do_ensure_private_deps(ctx):
        args.add("--implementation_deps_available")

    all_hdrs = target[CcInfo].compilation_context.headers.to_list()
    analysis_inputs = [processed_target] + ctx.files._config + processed_deps + processed_impl_deps + private_files + all_hdrs
    ctx.actions.run(
        executable = ctx.executable._dwyu_binary,
        inputs = analysis_inputs,
        outputs = [report_file],
        mnemonic = "CompareIncludesToDependencies",
        progress_message = "Analyze dependencies of {}".format(target.label),
        arguments = [args],
    )

    accumulated_reports = depset(direct = [report_file], transitive = _gather_transitive_reports(ctx))
    return [OutputGroupInfo(cc_dwyu_output = accumulated_reports)]
