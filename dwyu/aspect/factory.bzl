load("@rules_cc//cc:find_cc_toolchain.bzl", "use_cc_toolchain")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load("//dwyu/cc_info_mapping:providers.bzl", "DwyuCcInfoMappingInfo")
load(":dwyu.bzl", "dwyu_aspect_impl")

_DEFAULT_SKIPPED_TAGS = ["no-dwyu"]

def dwyu_aspect_factory(
        analysis_optimizes_impl_deps = False,
        analysis_reports_missing_direct_deps = True,
        analysis_reports_unused_deps = True,
        experimental_no_preprocessor = False,
        experimental_set_cplusplus = False,
        ignored_includes = None,
        no_preprocessor = False,
        recursive = False,
        skip_external_targets = False,
        skipped_tags = _DEFAULT_SKIPPED_TAGS,
        target_mapping = None,
        use_cpp_implementation = True,
        verbose = False):
    """
    Create a "**D**epend on **W**hat **Y**ou **U**se" (DWYU) aspect.

    Use the factory in a `.bzl` file to instantiate a DWYU aspect:
    ```starlark
    load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

    your_dwyu_aspect = dwyu_aspect_factory(<aspect_options>)
    ```

    Args:
        analysis_optimizes_impl_deps: Setting this to `True` will raise an error for `cc_library` targets where headers from a `deps` dependency are used only in private files.
                                      Such dependencies should be moved from `deps` to [implementation_deps](https://bazel.build/reference/be/c-cpp#cc_library.implementation_deps) to optimize the dependency graph of the project.<br>
                                      This flag can also be controlled in a Bazel config or on the command line via `--aspects_parameters=dwyu_analysis_optimizes_impl_deps=[True|False]`.<br>
                                      This feature is demonstrated in the [basic_usage example](/examples/basic_usage).

        analysis_reports_missing_direct_deps: Setting this to `True` will report include statements in the files of the target under inspection which are not covered by any of the direct dependencies of the target.
                                              This is useful to identify missing dependencies in the dependency graph of the project.<br>
                                              This flag can also be controlled in a Bazel config or on the command line via `--aspects_parameters=dwyu_analysis_reports_missing_direct_deps=[True|False]`.

        analysis_reports_unused_deps: Setting this to `True` will report dependencies which are not used in any of the files of the target under inspection as unused.
                                      This is useful to identify dependencies which can be removed from the dependency graph of the project.<br>
                                      This flag is only supported by the C++ based implementation of DWYU.<br>
                                      This flag can also be controlled in a Bazel config or on the command line via `--aspects_parameters=dwyu_analysis_reports_unused_deps=[True|False]`

        experimental_no_preprocessor: Deprecated flag.
                                      This feature is now stable.
                                      See [no_preprocessor](https://github.com/martis42/depend_on_what_you_use/blob/main/docs/dwyu_aspect.md#dwyu_aspect_factory-no_preprocessor)

        experimental_set_cplusplus: **DEPRECATED**: This flag will be removed together with the Python implementation.
                                    The new C++ based implementation will always try to set a proper `__cplusplus`.<br><br>
                                    `__cplusplus` is a macro defined by the compiler specifying if C++ is used to compile the file and which C++ standard is used.<br>
                                    DWYU cannot treat this like other preprocessor defines, as this is often not coming from the command line or the Bazel C++ toolchain.
                                    The compiler itself defines the value for `__cplusplus` and sets it internally during preprocessing.<br>
                                    This option enables a heuristic to set `__cplusplus` for the preprocessor used internally by DWYU.
                                    We look at the compilation command one would use to compile the code and look for `-std=..`.
                                    If it is is present and has a legal value, we deduce `__cplusplus` and set it for the preprocessing.
                                    If this logic fails, `__cplusplus` is not set.
                                    Users can provide their own value by setting `__cplusplus` via Bazel (e.g. via `--cxxopt=-D__cplusplus=42`) which will take precedence over the heuristic used by DWYU.
                                    This feature is demonstrated in the [set_cpp_standard example](/examples/set_cpp_standard).

        ignored_includes: By default, DWYU ignores all headers from the standard library when comparing include statements to the dependencies.
                          This list of headers can be seen in [std_header.py](/dwyu/aspect/private/analyze_includes/std_header.py).<br>
                          You can extend this list of ignored headers or replace it with a custom one by providing a json file with the information to this attribute.<br>
                          Specification of possible files in the json file:
                          <ul><li>
                            `ignore_include_paths` : List of include paths which are ignored by the analysis.
                            Setting this **disables ignoring the system and standard library include paths**.
                          </li><li>
                            `extra_ignore_include_paths` : List of concrete include paths which are ignored by the analysis.
                            Those are always ignored, no matter what other fields you provide.
                          </li><li>
                            `ignore_include_patterns` : List of patterns for include paths which are ignored by the analysis.
                            Patterns have to be compatible to Python [regex syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax).
                            The [match](https://docs.python.org/3/library/re.html#re.match) function is used to process the patterns.
                          </li></ul>
                          This feature is demonstrated in the [ignoring_includes example](/examples/ignoring_includes).

        no_preprocessor: This option disables the preprocessing step before discovering the include statements in the files under inspection.
                         When the preprocessing is disabled, DWYU still ignores commented include statements.
                         Using this option can speed up the DWYU analysis.<br>
                         When using this option, DWYU will no longer be able to correctly resolve conditional include logic (`#ifdef` around include statements) or any other preprocessor directives and macros influencing include statements.
                         A common example requiring preprocessing is having different include statements and Bazel target dependencies depending on whether the host is a Windows or Linux system.

        recursive: By default, the DWYU aspect analyzes only the target it is being applied to.
                   You can change this to recursively analyzing dependencies following the `deps` and `implementation_deps` attributes by setting this to True.<br>
                   This feature is demonstrated in the [recursion example](/examples/recursion).

        skip_external_targets: Sometimes external dependencies are not our under control and thus analyzing them is of little value.
                               If this flag is True, DWYU will automatically skip all targets from external workspaces.
                               This can be useful in combination with the recursive analysis mode.<br>
                               This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).

        skipped_tags: Do not execute the DWYU analysis on targets with at least one of those tags.
                      By default skips the analysis for targets tagged with 'no-dwyu'.<br>
                      This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).

        target_mapping: Accepts a [dwyu_make_cc_info_mapping](/docs/cc_info_mapping.md) target.
                        Allows virtually combining targets regarding which header can be provided by which dependency.
                        For the full details see the `dwyu_make_cc_info_mapping` documentation.<br>
                        This feature is demonstrated in the [target_mapping example](/examples/target_mapping).

        use_cpp_implementation: Set this to `False` to use the legacy Python based implementation.
                                If you have to use the Python implementation instead of the standard C++ based implementation, please create an issue with your problem in the [DWYU issue tracker](https://github.com/martis42/depend_on_what_you_use/issues).<br>
                                **The Python based implementation will be removed in a future release**!

        verbose: If `True`, print debugging information about the individual DWYU actions.<br>
                 This flag can also be controlled in a Bazel config or on the command line via `--aspects_parameters=dwyu_verbose=[True|False]`.

    Returns:
        Configured DWYU aspect
    """
    attr_aspects = []
    if recursive:
        attr_aspects = ["implementation_deps", "deps"]
    aspect_ignored_includes = [ignored_includes] if ignored_includes else []
    aspect_skipped_tags = _DEFAULT_SKIPPED_TAGS if skipped_tags == _DEFAULT_SKIPPED_TAGS else skipped_tags
    aspect_target_mapping = [target_mapping] if target_mapping else []
    if experimental_no_preprocessor:
        # buildifier: disable=print
        print("WARNING: 'experimental_no_preprocessor' is a deprecated flag due to the feature now being stable. Use 'no_preprocessor' instead.")
        no_preprocessor = True
    if use_cpp_implementation:
        target_processor = Label("//dwyu/aspect/private/process_target:main_cc")
        tool_preprocessing = Label("//dwyu/aspect/private/preprocessing:main_no_preprocessing") if no_preprocessor else Label("//dwyu/aspect/private/preprocessing:main")
        tool_analyze_includes = Label("//dwyu/aspect/private/analyze_includes:main")
    else:
        # buildifier: disable=print
        print("WARNING: Using the legacy Python based implementation, which will be removed in a future release. Please report an issue to DWYU if the new C++ based implementation does not work for you.")
        target_processor = Label("//dwyu/aspect/private/process_target:main_py")
        tool_preprocessing = Label("//dwyu/aspect/private/preprocessing:stub")
        tool_analyze_includes = Label("//dwyu/aspect/private/analyze_includes:analyze_includes")
    if not analysis_reports_missing_direct_deps and not use_cpp_implementation:
        fail("Disabling the reporting of missing direct dependencies is currently only supported in the C++ based implementation. Please set 'use_cpp_implementation' to True if you want to disable the reporting of missing direct dependencies.")
    if not analysis_reports_unused_deps and not use_cpp_implementation:
        fail("Disabling the reporting of unused dependencies is currently only supported in the C++ based implementation. Please set 'use_cpp_implementation' to True if you want to disable the reporting of unused dependencies.")

    return aspect(
        implementation = dwyu_aspect_impl,
        attr_aspects = attr_aspects,
        fragments = ["cpp"],
        required_providers = [CcInfo],
        toolchains = use_cc_toolchain(mandatory = True),
        attrs = {
            "dwyu_analysis_optimizes_impl_deps": attr.bool(
                default = analysis_optimizes_impl_deps,
            ),
            "dwyu_analysis_reports_missing_direct_deps": attr.bool(
                default = analysis_reports_missing_direct_deps,
            ),
            "dwyu_analysis_reports_unused_deps": attr.bool(
                default = analysis_reports_unused_deps,
            ),
            "dwyu_verbose": attr.bool(
                default = verbose,
            ),
            "_ignored_includes": attr.label_list(
                default = aspect_ignored_includes,
                allow_files = [".json"],
            ),
            "_no_preprocessor": attr.bool(
                default = no_preprocessor,
            ),
            "_recursive": attr.bool(
                default = recursive,
            ),
            "_set_cplusplus": attr.bool(
                default = experimental_set_cplusplus,
            ),
            "_skip_external_targets": attr.bool(
                default = skip_external_targets,
            ),
            "_skipped_tags": attr.string_list(
                default = aspect_skipped_tags,
            ),
            "_target_mapping": attr.label_list(
                providers = [DwyuCcInfoMappingInfo],
                default = aspect_target_mapping,
            ),
            "_tool_analyze_includes": attr.label(
                default = tool_analyze_includes,
                executable = True,
                cfg = "exec",
                doc = "Main logic for the analysis done by this aspect. This compares the include statements in the code and compares them to the available dependencies.",
            ),
            "_tool_preprocessing": attr.label(
                default = tool_preprocessing,
                executable = True,
                cfg = "exec",
                doc = "Preprocess the source code under inspection to resolve conditional preprocessor statements and discover include statements.",
            ),
            "_tool_process_target": attr.label(
                default = target_processor,
                executable = True,
                cfg = "exec",
                doc = "Tool for processing the target under inspection and its dependencies. We have to perform this" +
                      " as separate action, since otherwise we can't look into TreeArtifact sources.",
            ),
            "_use_cpp_implementation": attr.bool(
                default = use_cpp_implementation,
            ),
        },
    )
