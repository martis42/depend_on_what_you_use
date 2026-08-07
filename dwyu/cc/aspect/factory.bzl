load("@rules_cc//cc:find_cc_toolchain.bzl", "use_cc_toolchain")
load("@rules_cc//cc/common:cc_info.bzl", "CcInfo")
load("//dwyu/cc/cc_info_mapping:providers.bzl", "DwyuCcInfoMappingInfo")
load("//dwyu/private:utils.bzl", "unique_list")
load(":dwyu.bzl", "PREPROCESSOR_MODES", "dwyu_cc_aspect_impl")

_LEGACY_SKIPPED_TAGS = ["no-dwyu"]
_MANDATORY_SKIPPED_TAGS = ["dwyu:skip"]
_DEFAULT_SKIPPED_TAGS = _MANDATORY_SKIPPED_TAGS + _LEGACY_SKIPPED_TAGS

def _validate_skip_targets(patterns):
    """
    We support only a small subset of the Bazel target pattern syntax. Everything else is rejected at load time
    instead of silently never matching anything.
    """
    for pattern in patterns:
        if "//" not in pattern:
            fail("Invalid 'skip_targets' pattern '{}'. Patterns have to contain '//'.".format(pattern))
        if "*" in pattern:
            fail("Invalid 'skip_targets' pattern '{}'. Wildcards are not supported.".format(pattern))
        if pattern.startswith("-"):
            fail("Invalid 'skip_targets' pattern '{}'. Negative patterns are not supported.".format(pattern))
        _, _, rest = pattern.partition("//")
        if "..." in rest:
            if not (rest == "..." or rest.endswith("/...")):
                fail("Invalid 'skip_targets' pattern '{}'. '...' is only allowed as the final path segment.".format(pattern))
        elif ":" not in rest:
            fail("Invalid 'skip_targets' pattern '{}'. Patterns have to name a target explicitly (e.g. '//foo:bar' or '//foo:all').".format(pattern))

def dwyu_cc_aspect_factory(
        analysis_ignores_private_headers_from_deps = True,
        analysis_optimizes_impl_deps = False,
        analysis_reports_missing_direct_deps = True,
        analysis_reports_unused_deps = True,
        ignored_includes = None,
        ignored_unused_deps = [],
        preprocessing_mode = "full",
        recursive = False,
        recursion_stops_on_skip = False,
        skip_external_targets = False,
        skip_tags = _DEFAULT_SKIPPED_TAGS,
        skip_targets = [],
        skip_toolchain_features = [],
        skipped_tags = [],
        target_mapping = None,
        verbose = False):
    """
    Create and configure a "**D**epend on **W**hat **Y**ou **U**se" (DWYU) aspect.

    You might have targets which require different DWYU settings than the ones set by you with the aspect factory.
    If this is the case for a separate part of your project, an easy solution can be to create a second aspect instance with different settings and use that for the targets in question.
    However, if the issue is with individual targets, you can also use the following tags to override the DWYU settings for those specific targets.
    Using tags to control the DWYU behavior is demonstrated in the [configuration_via_tags example](/examples/configuration_via_tags).<br>
    The detailed description for the features controlled by these tags can be found below in the documentation of the aspect factory parameters.
    If a tag sets a single value attribute, the tag value will override the value set by the aspect factory or via `--aspects_parameters`.
    If a tag sets a list attribute, the tag value will be appended to the list set by the aspect factory.

    | Tag | Description |
    |---|---|
    | `dwyu:skip`                                            | Do not perform any DWYU analysis. |
    | `dwyu:ignore_private_headers_from_deps=[True\\|False]` | Control whether to consider private headers from the `srcs` attribute of dependencies. |
    | `dwyu:optimize_impl_deps=[True\\|False]`               | Control optimizing implementation dependencies. |
    | `dwyu:report_missing_direct_deps=[True\\|False]`       | Control reporting missing direct dependencies. |
    | `dwyu:report_unused_deps=[True\\|False]`               | Control reporting unused dependencies. |
    | `dwyu:ignore_include=<include>`                        | Ignore the specified include for the _missing direct dependencies_ check. Provide without quoting (aka `<` or `"`). Does not support setting patterns. Multiple uses are accumulated. |
    | `dwyu:ignore_unused_dep=<dep>`                         | Ignore the specified dependency for the _unused dependencies_ check. Has to use the canonical repo name. The examples show an elegant way to do this. Multiple uses are accumulated. |
    | `dwyu:preprocessing_mode=<mode>`                       | Control the preprocessing mode. |

    Args:
        analysis_ignores_private_headers_from_deps: Setting this to `False` will allow headers listed in the `srcs` attributes of a dependency to fulfill the DWYU checks on top of those from the `hdrs` attribute.
                                                    By default, DWYU uses only headers from the `hdrs` attribute.</br>
                                                    Strictly speaking, using headers from the `srcs` attribute of a dependency is wrong, as they are an implementation detail of the dependency.
                                                    However, Bazel does not enforce this and forwards those private headers to the compile step.
                                                    Use this flag if you have code outside your control using private headers or simply are not interested in the distinction of public and private headers.</br>
                                                    This flag can also be controlled in a Bazel config or on the command line via `--aspects_parameters=dwyu_analysis_ignores_private_headers_from_deps=[True|False]`.

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

        ignored_unused_deps: There might be dependencies triggering the DWYU check for unused dependencies which you want to ignore.
                             You can provide here a list of targets which will be ignored for the unused dependencies check.<br>
                             You have to use the Label constructor, you can't use bare strings.
                             For example: `ignored_unused_deps = [Label("//some:target")]`

        preprocessing_mode: DWYU performs a preprocessing step on the code to extract the relevant include statements.
                            This options allows configuring different strategies for this with varying speed and capabilities tradeoffs.<br>
                            We perform a preprocessing to be able to ignore CC toolchain headers and resolve conditional include logic (`#ifdef` around include statements) and other preprocessor directives influencing include statements (e.g. a macro defining the to be included header path).<br>
                            The available preprocessing modes are:
                            <ul><li>
                              `full`: (Default).<br>
                              In this mode, we use the [`boost::wave`](https://github.com/boostorg/wave) library to preprocess the code.
                              This also involves recursively preprocessing all included header files.
                              While this mode is the slowest, it is able to handle most kinds of conditional include logic or macros influencing include statements.<br>
                              If preprocessing a file hits a construct `boost::wave` cannot evaluate (e.g. `__has_include`), we automatically fall back to extracting the include statements of the affected file as the `fast` mode does.
                              This way include statements are never silently dropped due to such constructs, at the cost of conditional include logic not being resolved for the affected files.
                            </li><li>
                              `ignore_system_includes`: Works similar to `full`, but should be faster for most projects.<br>
                              In this mode, we do not look into header files included as system includes (aka using the '<>' notation) during the preprocessing step.
                              Often, the system includes are not relevant for the conditional include logic in the user's code.
                              At the same time they can point to large and complex headers which take a lot of time to preprocess (e.g. <gtest/gtest.h>).<br>
                              The automatic fallback to extracting include statements as the `fast` mode does works as described for `full`.
                            </li><li>
                              `fast`: The fastest preprocessing mode, which does however not support conditional include logic or macros influencing include statements.<br>
                              In this mode, we do not use `boost::wave` to preprocess the code.
                              We simply extract all existing include statements without looking into the recursively included headers.
                            </li></ul>

        recursive: By default, the DWYU aspect analyzes only the target it is being applied to.
                   You can change this to recursively analyzing dependencies following the `deps` and `implementation_deps` attributes by setting this to True.<br>
                   This feature is demonstrated in the [recursion example](/examples/recursion).

        recursion_stops_on_skip: If `True`, skipping a target will also stop the recursive analysis of its dependencies.
                                 This does not just influence the behavior of the `skip_*` options, but also skipping to inbuilt logic (e.g. skipping incompatible rule types).

        skip_external_targets: Sometimes external dependencies are not our under control and thus analyzing them is of little value.
                               If this flag is True, DWYU will automatically skip all targets from external workspaces.
                               This can be useful in combination with the recursive analysis mode.<br>
                               This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).

        skip_tags: Do not execute the DWYU analysis on targets with at least one of those tags.
                   Targets tagged with `dwyu:skip` are always skipped, no matter what is configured here.<br>
                   This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).

        skip_targets: Do not execute the DWYU analysis on targets matching at least one of the given target patterns.
                      In contrast to `skipped_tags`, this excludes targets without changing their `BUILD` files.
                      This makes it a good fit for migrating an existing project to DWYU, where the list of not yet compliant targets should live in a single reviewable place instead of being scattered across the whole project.<br>
                      Only a small subset of the [Bazel target pattern syntax](https://bazel.build/run/build#specifying-build-targets) is supported:
                      <ul><li>
                        `//foo:bar` : Exactly this target.
                      </li><li>
                        `//foo:all` : Every target in exactly this package.
                      </li><li>
                        `//foo/...` : Every target in this package and all its subpackages.
                      </li><li>
                        `//...` : Every target in the repository.
                      </li></ul>
                      Neither `*` globbing nor negative patterns (`-//foo:bar`) are supported.
                      Invalid patterns cause an error while loading the aspect.<br>
                      Without an `@repo` prefix a pattern refers to the main repository.
                      Patterns for external repositories have to use the canonical repository name (e.g. `@rules_cc+`), not the apparent one (e.g. `@rules_cc`).
                      The canonical name depends on the Bazel version and the module resolution, thus we advise using `skip_external_targets` if you want to exclude external repositories in general.<br>
                      In contrast to the other skipping mechanisms, the DWYU reports of the dependencies are still propagated.
                      Meaning, in the recursive analysis mode excluding a target does not stop the analysis of the targets below it.<br>
                      This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).

        skip_toolchain_features: A list of C++ toolchain feature strings that control when the DWYU analysis is skipped.
                                 When a feature name is prefixed with `-` (e.g. `-layering_check`), the analysis is skipped if that feature is **disabled**.
                                 When a feature name has no prefix (e.g. `some_feature`), the analysis is skipped if that feature is **enabled**.
                                 This allows gating DWYU on the state of C++ toolchain features configured via the standard `features` attribute.<br>
                                 Please note, this is based on the features the active toolchain understands and not string comparison done with the `features` attribute values.
                                 Meaning, changing the toolchain can change the skipping behavior, even if the `features` attributes of your cc_* targets remain constant.

        skipped_tags: Deprecated option, use `skip_tags` instead.
                      Will be replaced in a future release.

        target_mapping: Accepts a [dwyu_make_cc_info_mapping](/docs/api/cc_info_mapping.md) target.
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

    if skip_tags != _DEFAULT_SKIPPED_TAGS and skipped_tags:
        fail("Both 'skip_tags' and 'skipped_tags' are set. Please use only 'skip_tags'.")
    if skipped_tags:
        # buildifier: disable=print
        print("DWYU - WARNING: Option 'skipped_tags' is deprecated and will be removed in a future release. Please use 'skip_tags' instead.")
        aspect_skip_tags = unique_list(skipped_tags, _MANDATORY_SKIPPED_TAGS)
    else:
        aspect_skip_tags = _DEFAULT_SKIPPED_TAGS if skip_tags == _DEFAULT_SKIPPED_TAGS else unique_list(skip_tags, _MANDATORY_SKIPPED_TAGS)

    aspect_target_mapping = [target_mapping] if target_mapping else []

    if preprocessing_mode not in PREPROCESSOR_MODES:
        fail("Provided invalid value '{}' for 'preprocessing_mode'. Supported values are {}".format(preprocessing_mode, PREPROCESSOR_MODES))

    _validate_skip_targets(skip_targets)

    return aspect(
        implementation = dwyu_cc_aspect_impl,
        attr_aspects = attr_aspects,
        fragments = ["cpp"],
        required_providers = [CcInfo],
        toolchains = use_cc_toolchain(mandatory = True),
        attrs = {
            "dwyu_analysis_ignores_private_headers_from_deps": attr.bool(
                default = analysis_ignores_private_headers_from_deps,
            ),
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
            "_ignored_unused_deps": attr.string_list(
                default = [str(dep) for dep in ignored_unused_deps],
            ),
            "_preprocessing_mode": attr.string(
                default = preprocessing_mode,
            ),
            "_recursion_stops_on_skip": attr.bool(
                default = recursion_stops_on_skip,
            ),
            "_recursive": attr.bool(
                default = recursive,
            ),
            "_skip_external_targets": attr.bool(
                default = skip_external_targets,
            ),
            "_skip_tags": attr.string_list(
                default = aspect_skip_tags,
            ),
            "_skip_targets": attr.string_list(
                default = skip_targets,
            ),
            "_skip_toolchain_features": attr.string_list(
                default = skip_toolchain_features,
            ),
            "_target_mapping": attr.label_list(
                providers = [DwyuCcInfoMappingInfo],
                default = aspect_target_mapping,
            ),
            "_tool_analyze_includes": attr.label(
                default = Label("//dwyu/cc/aspect/private/analyze_includes:main"),
                executable = True,
                cfg = "exec",
                doc = "Main logic for the analysis done by this aspect. This compares the include statements in the code and compares them to the available dependencies.",
            ),
            "_tool_preprocessing": attr.label(
                default = Label("//dwyu/cc/aspect/private/preprocessing:main"),
                executable = True,
                cfg = "exec",
                doc = "Preprocess the source code under inspection to resolve conditional preprocessor statements and discover include statements.",
            ),
            "_tool_process_target": attr.label(
                default = Label("//dwyu/cc/aspect/private/process_target:main"),
                executable = True,
                cfg = "exec",
                doc = "Tool for processing the target under inspection and its dependencies. We have to perform this" +
                      " as separate action, since otherwise we can't look into TreeArtifact sources.",
            ),
        },
    )
