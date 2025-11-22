load("@rules_cc//cc:action_names.bzl", "CPP_COMPILE_ACTION_NAME")
load("@rules_cc//cc:find_cc_toolchain.bzl", "find_cc_toolchain")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load("//dwyu/cc_info_mapping:providers.bzl", "DwyuCcInfoMappingInfo")
load("//dwyu/cc_toolchain_headers:providers.bzl", "DwyuCcToolchainHeadersInfo")
load("//dwyu/private:utils.bzl", "make_param_file_args")

# Based on those references:
# https://gcc.gnu.org/onlinedocs/cpp/Standard-Predefined-Macros.html
# https://clang.llvm.org/cxx_status.html
# https://gcc.gnu.org/onlinedocs/gcc/C-Dialect-Options.html
# https://learn.microsoft.com/en-us/cpp/build/reference/std-specify-language-standard-version?view=msvc-170
#
# We ignore the fuzzy variants (e.g. 'c++1X' or 'c++2X') as their values seem to be not constant but depend on the
# compiler version.
_STD_FLAG_TO_STANDARD = {
    "c++03": 199711,
    "c++11": 201103,
    "c++14": 201402,
    "c++17": 201703,
    "c++20": 202002,
    "c++23": 202302,
    "c++98": 199711,
    "gnu++03": 199711,
    "gnu++11": 201103,
    "gnu++14": 201402,
    "gnu++17": 201703,
    "gnu++20": 202002,
    "gnu++23": 202302,
    "gnu++98": 199711,
}

def _is_external(ctx):
    return ctx.label.workspace_root.startswith("external")

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

def _get_includes(ctx, target_cc):
    includes = [target_cc.includes]
    quote_includes = [target_cc.quote_includes]
    external_includes = [target_cc.external_includes] if hasattr(target_cc, "external_includes") else []
    system_includes = [target_cc.system_includes]
    if hasattr(ctx.rule.attr, "implementation_deps"):
        # Because of bug https://github.com/bazelbuild/bazel/issues/19663 the compilation context is not actually
        # containing the information to compile a target when it is using implementation_deps. Thus, we have to
        # aggregate this information ourselves.
        for impl_dep in ctx.rule.attr.implementation_deps:
            impl_dep_cc = impl_dep[CcInfo].compilation_context
            if impl_dep_cc.includes:
                includes.append(impl_dep_cc.includes)
            if impl_dep_cc.quote_includes:
                quote_includes.append(impl_dep_cc.quote_includes)
            if hasattr(impl_dep_cc, "external_includes") and impl_dep_cc.external_includes:
                external_includes.append(impl_dep_cc.external_includes)
            if impl_dep_cc.system_includes:
                system_includes.append(impl_dep_cc.system_includes)

    return includes, quote_includes, external_includes, system_includes

def _process_target(ctx, target, defines, output_path, is_target_under_inspection, verbose):
    processing_output = ctx.actions.declare_file(output_path)
    cc_context = target.cc_info.compilation_context
    header_files = _get_relevant_header(
        target_context = cc_context,
        is_target_under_inspection = is_target_under_inspection,
    )

    args = make_param_file_args(ctx)
    args.add("--target", str(target.label))
    args.add("--output", processing_output)
    args.add_all("--header_files", header_files, expand_directories = True, omit_if_empty = False)
    if is_target_under_inspection:
        includes, quote_includes, external_includes, system_includes = _get_includes(ctx, cc_context)
        args.add_all("--includes", depset(transitive = includes), omit_if_empty = False)
        args.add_all("--quote_includes", depset(transitive = quote_includes), omit_if_empty = False)
        args.add_all("--external_includes", depset(transitive = external_includes), omit_if_empty = False)
        args.add_all("--system_includes", depset(transitive = system_includes), omit_if_empty = False)
        args.add_all("--defines", defines)
    if verbose:
        args.add("--verbose")

    ctx.actions.run(
        inputs = header_files,
        executable = ctx.executable._tool_process_target,
        arguments = [args],
        mnemonic = "DwyuProcessTargetInfo",
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
    defines = {}

    for cflag in compiler_flags:
        # gcc/clang use '-U'. MSVC uses '/U'.
        if cflag.startswith(("-U", "/U")):
            undefine = cflag[2:]
            undefine_name = undefine.split("=", 1)[0]
            if undefine_name in defines.keys():
                defines.pop(undefine_name)

        # gcc/clang use '-D'. MSVC uses '/D'.
        if cflag.startswith(("-D", "/D")):
            define = cflag[2:]
            define_name = define.split("=", 1)[0]

            # For the cc_* rules copts attribute users have to double escape the quote character to define macros pointing to strings.
            # Our own processing however cannot handle double escaped characters and needs single escaping.
            defines[define_name] = define.replace('\\"', '\"')

    return defines.values()

def extract_cpp_standard_from_compiler_flags(compiler_flags):
    cpp_standard = None

    for cflag in compiler_flags:
        standard_value = None

        # gcc/clang
        if cflag.startswith("-std="):
            standard_value = cflag.split("=", 1)[1]

        # MSVC
        if cflag.startswith("/std:"):
            standard_value = cflag.split(":", 1)[1]

        if standard_value:
            standard = _STD_FLAG_TO_STANDARD.get(standard_value, None)
            if standard:
                cpp_standard = standard
            elif not cpp_standard:
                # We see a standard flag, but don't understands its value. We ensure the C++ standard macro is defined,
                # even if we can't define its exact value.
                cpp_standard = 1

    return cpp_standard

def _is_c_file(file):
    """
    Heuristic for finding C files by looking for the established file extensions.
    """
    return file.extension in ["h", "c"]

def _gather_defines(ctx, target_compilation_context, target_files):
    """
    We extract the relevant defines from the compiler command line flags. We utilize the compiler flags since the
    toolchain can set defines which are not available through CcInfo or the cpp fragments. Furthermore, defines
    potentially overwrite or deactivate each other depending on the order in which they appear in the compiler
    command. Thus, this is the only way to make sure DWYU analyzes what would actually happen during compilation.
    """

    cc_toolchain = find_cc_toolchain(ctx)

    feature_configuration = cc_common.configure_features(
        ctx = ctx,
        cc_toolchain = cc_toolchain,
        requested_features = ctx.features,
        unsupported_features = ctx.disabled_features,
    )

    defines = []
    if hasattr(ctx.rule.attr, "implementation_deps"):
        # Because of bug https://github.com/bazelbuild/bazel/issues/19663 the compilation context is not actually
        # containing the information to compile a target when it is using implementation_deps. Thus, we have to
        # aggregate this information ourselves.
        for impl_dep in ctx.rule.attr.implementation_deps:
            impl_dep_cc = impl_dep[CcInfo].compilation_context
            if impl_dep_cc.defines:
                defines.append(impl_dep_cc.defines)

    # Add the target defines last in case the order is important for undefining already defined macros
    defines.append(target_compilation_context.defines)

    compile_variables = cc_common.create_compile_variables(
        feature_configuration = feature_configuration,
        cc_toolchain = cc_toolchain,
        user_compile_flags = ctx.rule.attr.copts + ctx.fragments.cpp.cxxopts + ctx.fragments.cpp.copts,
        preprocessor_defines = depset(transitive = defines + [target_compilation_context.local_defines]),
    )

    # We cannot directly work with 'compile_variables' in Starlark, thus we translate them into string representation
    compiler_command_line_flags = cc_common.get_memory_inefficient_command_line(
        feature_configuration = feature_configuration,
        action_name = CPP_COMPILE_ACTION_NAME,
        variables = compile_variables,
    )

    defines = extract_defines_from_compiler_flags(compiler_command_line_flags)

    if ctx.attr._set_cplusplus:
        cpp_standard = None
        compiler_cpp_standard = extract_cpp_standard_from_compiler_flags(compiler_command_line_flags)

        # If we can extract a c++ standard from the compiler invocation, we use it as we consider this our most reliable
        # source of information
        if compiler_cpp_standard:
            cpp_standard = compiler_cpp_standard

        # If we could not determine the C++ standard based on the compiler arguments, we use a heuristic based on the
        # file types. If any file extension other than ['.h', '.c'] is used, we assume C++.
        if not cpp_standard:
            # We don't know the exact C++ standard, but at least we can enable preprocessor control statements caring
            # only about '__cplusplus' being defined at all or not.
            if not all([_is_c_file(file) for file in target_files]):
                cpp_standard = 1

        # If we assume this is a C++ compilation, add the corresponding constant to the defines list
        if cpp_standard:
            defines.append("__cplusplus={}".format(cpp_standard))

    return defines

def _exchange_cc_info(deps, mapping):
    transformed = []
    mapping_info = mapping[0][DwyuCcInfoMappingInfo].mapping
    for dep in deps:
        if dep.label in mapping_info:
            transformed.append(struct(label = dep.label, cc_info = mapping_info[dep.label]))
        else:
            transformed.append(struct(label = dep.label, cc_info = dep[CcInfo]))
    return transformed

def _preprocess_deps(ctx):
    """
    Normally this function does nothing and simply stores dependencies and their CcInfo providers in a specific format.
    If the user chooses to use the target mapping feature, we exchange here the CcInfo provider for some targets with a
    different one.
    """
    target_impl_deps = []
    if ctx.attr._target_mapping:
        target_deps = _exchange_cc_info(deps = ctx.rule.attr.deps, mapping = ctx.attr._target_mapping)
        if hasattr(ctx.rule.attr, "implementation_deps"):
            target_impl_deps = _exchange_cc_info(deps = ctx.rule.attr.implementation_deps, mapping = ctx.attr._target_mapping)
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

def _dywu_results_from_deps(deps):
    """
    We cannot rely on DWYU being executed on the dependencies as analysis of the dependency might have been skipped.
    """
    return [dep[OutputGroupInfo].dwyu for dep in deps if hasattr(dep[OutputGroupInfo], "dwyu")]

def _gather_transitive_reports(ctx):
    """
    In recursive operation mode we have to propagate the DWYU report files of all transitive dependencies to ensure
    the DWYU actions run for all targets. Not doing this will cause DWYU not being executed at all as without returning
    the report files Bazel prunes the DWYU actions.
    """
    reports = []
    if ctx.attr._recursive:
        reports.extend(_dywu_results_from_deps(ctx.rule.attr.deps))
        if hasattr(ctx.rule.attr, "implementation_deps"):
            reports.extend(_dywu_results_from_deps(ctx.rule.attr.implementation_deps))
    return reports

def _extract_includes_from_files(ctx, target, files, defines, cc_toolchain):
    """
    For each given file perform a preprocessing step to find all relevant include statements
    """

    # Work around the bug described in https://github.com/bazelbuild/bazel/issues/19663
    # Implementation_deps are not added to CcInfo.compilation_context
    if hasattr(ctx.rule.attr, "implementation_deps"):
        impl_deps_hdrs = depset(direct = [], transitive = [dep[CcInfo].compilation_context.headers for dep in ctx.rule.attr.implementation_deps])
    else:
        impl_deps_hdrs = depset(direct = [], transitive = [])

    # Based on https://bazel.build/rules/lib/builtins/CompilationContext.html the logic is:
    # - includes -> Search paths for resolving include statements using angle brackets or quotes
    # - quote_includes -> Search paths for resolving include statements using quotes
    # - system_includes -> Search paths for resolving include statements using angle brackets
    # - external_includes -> Special list controlled by a CC toolchain feature.
    #                        Search paths for resolving include statements using angle brackets for external dependencies
    #
    # We are ignoring 'framework_includes'. Our preprocessor does not support this.
    # Furthermore, this is mostly used for the system and toolchain headers as well as external dependencies.
    # We want to ignore system and toolchain headers either way.
    includes, quote_includes, external_includes, system_includes = _get_includes(ctx, target[CcInfo].compilation_context)
    include_paths = depset(transitive = quote_includes + includes)
    system_include_paths = depset(transitive = system_includes + external_includes + includes)

    preprocessor_results = []
    for file in files:
        pp_output = ctx.actions.declare_file("{}_{}.dwyu_ppr.json".format(target.label.name, file.basename))

        # The source files could be a TreeArtifact! Thus, process each file as list, although we want to process the individual source files in parallel by default.
        args = make_param_file_args(ctx)
        args.add_all("--files", [file])
        args.add_all("--include_paths", include_paths)
        args.add_all("--system_include_paths", system_include_paths)
        args.add_all("--defines", defines)
        args.add("--output", pp_output)
        if ctx.attr._verbose:
            args.add("--verbose")

        inputs = depset(direct = files, transitive = [target[CcInfo].compilation_context.headers, impl_deps_hdrs, cc_toolchain.all_files])
        ctx.actions.run(
            executable = ctx.executable._tool_preprocessing,
            inputs = inputs,
            outputs = [pp_output],
            mnemonic = "DwyuProcessSourceFile",
            arguments = [args],
        )

        preprocessor_results.append(pp_output)

    return preprocessor_results

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

    # If configured, skip external targets
    if ctx.attr._skip_external_targets and _is_external(ctx):
        return []

    # Skip targets which explicitly opt-out
    if any([tag in ctx.attr._skipped_tags for tag in ctx.rule.attr.tags]):
        return []

    public_files, private_files = _get_target_sources(ctx.rule)

    # We skip targets which have no source files. cc_* targets can also be of value if they only specify the 'deps'
    # attribute without own sources. But those targets are not of interest for DWYU.
    if not public_files and not private_files:
        return []

    defines = _gather_defines(
        ctx,
        target_compilation_context = target[CcInfo].compilation_context,
        target_files = public_files + private_files,
    )
    processed_target = _process_target(
        ctx,
        target = struct(label = target.label, cc_info = target[CcInfo]),
        defines = defines,
        output_path = "{}_processed_target_under_inspection.json".format(target.label.name),
        is_target_under_inspection = True,
        verbose = ctx.attr._verbose,
    )

    target_deps, target_impl_deps = _preprocess_deps(ctx)

    # TODO Investigate if we can prevent running this multiple times for the same dep if multiple
    #      target_under_inspection have the same dependency
    processed_deps = _process_dependencies(ctx, target = target, deps = target_deps, verbose = ctx.attr._verbose)
    processed_impl_deps = _process_dependencies(ctx, target = target, deps = target_impl_deps, verbose = ctx.attr._verbose)

    report_file = ctx.actions.declare_file("{}_dwyu_report.json".format(target.label.name))

    if ctx.attr._use_cpp_implementation:
        cc_toolchain = find_cc_toolchain(ctx)

        preprocessed_public_files = _extract_includes_from_files(ctx = ctx, target = target, files = public_files, defines = defines, cc_toolchain = cc_toolchain)
        preprocessed_private_files = _extract_includes_from_files(ctx = ctx, target = target, files = private_files, defines = defines, cc_toolchain = cc_toolchain)

        args = make_param_file_args(ctx)
        args.add("--report", report_file)
        args.add_all("--preprocessed_public_files", preprocessed_public_files, omit_if_empty = False)
        args.add_all("--preprocessed_private_files", preprocessed_private_files, omit_if_empty = False)
        args.add("--target_under_inspection", processed_target)
        args.add_all("--deps", processed_deps, omit_if_empty = False)
        args.add_all("--implementation_deps", processed_impl_deps, omit_if_empty = False)
        if ctx.attr._ignored_includes:
            args.add("--ignored_includes_config", ctx.files._ignored_includes[0])
        if _do_ensure_private_deps(ctx):
            args.add("--implementation_deps_available")
        if ctx.attr._ignore_cc_toolchain_headers:
            args.add("--toolchain_headers_info", ctx.attr._cc_toolchain_headers[DwyuCcToolchainHeadersInfo].headers_info)

        analysis_inputs = depset(
            direct = [processed_target, ctx.attr._cc_toolchain_headers[DwyuCcToolchainHeadersInfo].headers_info] + public_files + private_files + processed_deps + processed_impl_deps + ctx.files._ignored_includes + preprocessed_public_files + preprocessed_private_files,
            transitive = [target[CcInfo].compilation_context.headers],
        )
        ctx.actions.run(
            executable = ctx.executable._tool_analyze_preprocessing_results,
            inputs = analysis_inputs,
            outputs = [report_file],
            mnemonic = "DwyuAnalyzeTarget",
            progress_message = "Analyze dependencies of {}".format(target.label),
            arguments = [args],
        )

    else:
        args = make_param_file_args(ctx)
        args.add("--report", report_file)
        args.add_all("--public_files", public_files, expand_directories = True, omit_if_empty = False)
        args.add_all("--private_files", private_files, expand_directories = True, omit_if_empty = False)
        args.add("--target_under_inspection", processed_target)
        args.add_all("--deps", processed_deps, omit_if_empty = False)
        args.add_all("--implementation_deps", processed_impl_deps, omit_if_empty = False)
        if ctx.attr._ignored_includes:
            args.add("--ignored_includes_config", ctx.files._ignored_includes[0])
        if _do_ensure_private_deps(ctx):
            args.add("--implementation_deps_available")
        if ctx.attr._no_preprocessor:
            args.add("--no_preprocessor")
        if ctx.attr._ignore_cc_toolchain_headers:
            args.add("--toolchain_headers_info", ctx.attr._cc_toolchain_headers[DwyuCcToolchainHeadersInfo].headers_info)

        # Skip 'public_files' as those are included in the targets CcInfo.compilation_context.headers
        analysis_inputs = depset(
            direct = [processed_target, ctx.attr._cc_toolchain_headers[DwyuCcToolchainHeadersInfo].headers_info] + private_files + processed_deps + processed_impl_deps + ctx.files._ignored_includes,
            transitive = [target[CcInfo].compilation_context.headers],
        )
        ctx.actions.run(
            executable = ctx.executable._dwyu_binary,
            inputs = analysis_inputs,
            outputs = [report_file],
            mnemonic = "DwyuAnalyzeIncludes",
            progress_message = "Analyze dependencies of {}".format(target.label),
            arguments = [args],
        )

    accumulated_reports = depset(direct = [report_file], transitive = _gather_transitive_reports(ctx))
    return [OutputGroupInfo(dwyu = accumulated_reports)]
