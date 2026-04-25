load("@rules_cc//cc:find_cc_toolchain.bzl", "use_cc_toolchain")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load("//dwyu/cc_info_mapping:providers.bzl", "DwyuCcInfoMappingInfo")
load(":dwyu.bzl", "dwyu_aspect_impl")

_DEFAULT_SKIPPED_TAGS = ["no-dwyu"]

def dwyu_aspect_factory(
        analysis_optimizes_impl_deps = False,
        analysis_reports_missing_direct_deps = True,
        analysis_reports_unused_deps = True,
        ignored_includes = None,
        no_preprocessor = False,
        recursive = False,
        skip_external_targets = False,
        skip_toolchain_features = [],
        skipped_tags = _DEFAULT_SKIPPED_TAGS,
        target_mapping = None,
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

        ignored_includes: The DWYU analysis ignores all files which are provided by the Bazel CC toolchain (e.g. the standard library headers).
                          If you want to ignore additional headers, you can provide a json file with the information to this attribute.<br>
                          The ignore logic works on the path provided to the include statement, e.g. `#include <foo/bar.h>` will be checked against the ignore list as `foo/bar.h`.<br>
                          Json file specification:
                          <ul><li>
                            `ignore_include_paths` : List of include paths which are ignored by the analysis.
                          </li><li>
                            `ignore_include_patterns` : List of patterns which are ignored by the analysis.
                            The [boost regex library](https://www.boost.org/doc/libs/latest/libs/regex/doc/html/index.html) is used to parse the patterns.
                            The [boost::regex_search](https://www.boost.org/doc/libs/latest/libs/regex/doc/html/boost_regex/ref/regex_search.html) function is used to compare the patterns to the include statements.
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

        skip_toolchain_features: A list of C++ toolchain feature strings that control when the DWYU analysis is skipped.
                                 When a feature name is prefixed with `-` (e.g. `-layering_check`), the analysis is skipped if that feature is **disabled**.
                                 When a feature name has no prefix (e.g. `some_feature`), the analysis is skipped if that feature is **enabled**.
                                 This allows gating DWYU on the state of C++ toolchain features configured via the standard `features` attribute.<br>
                                 Please note, this is based on the features the active toolchain understands and not string comparison done with the `features` attribute values.
                                 Meaning, changing the toolchain can change the skipping behavior, even if the `features` attributes of your cc_* targets remain constant.

        skipped_tags: Do not execute the DWYU analysis on targets with at least one of those tags.
                      By default skips the analysis for targets tagged with 'no-dwyu'.<br>
                      This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).

        target_mapping: Accepts a [dwyu_make_cc_info_mapping](/docs/cc_info_mapping.md) target.
                        Allows virtually combining targets regarding which header can be provided by which dependency.
                        For the full details see the `dwyu_make_cc_info_mapping` documentation.<br>
                        This feature is demonstrated in the [target_mapping example](/examples/target_mapping).

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
    tool_preprocessing = Label("//dwyu/aspect/private/preprocessing:main_no_preprocessing") if no_preprocessor else Label("//dwyu/aspect/private/preprocessing:main")

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
            "_skip_external_targets": attr.bool(
                default = skip_external_targets,
            ),
            "_skip_toolchain_features": attr.string_list(
                default = skip_toolchain_features,
            ),
            "_skipped_tags": attr.string_list(
                default = aspect_skipped_tags,
            ),
            "_target_mapping": attr.label_list(
                providers = [DwyuCcInfoMappingInfo],
                default = aspect_target_mapping,
            ),
            "_tool_analyze_includes": attr.label(
                default = Label("//dwyu/aspect/private/analyze_includes:main"),
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
                default = Label("//dwyu/aspect/private/process_target:main_cc"),
                executable = True,
                cfg = "exec",
                doc = "Tool for processing the target under inspection and its dependencies. We have to perform this" +
                      " as separate action, since otherwise we can't look into TreeArtifact sources.",
            ),
        },
    )
