load("@depend_on_what_you_use//src/cc_info_mapping:providers.bzl", "DwyuCcInfoRemappingsInfo")
load(":dwyu.bzl", "dwyu_aspect_impl")

_DEFAULT_SKIPPED_TAGS = ["no-dwyu"]

def dwyu_aspect_factory(
        ignored_includes = None,
        recursive = False,
        skip_external_targets = False,
        skipped_tags = _DEFAULT_SKIPPED_TAGS,
        target_mapping = None,
        use_implementation_deps = False,
        verbose = False):
    """
    Create a "Depend on What You Use" (DWYU) aspect.

    Use the factory in a `.bzl` file to instantiate a DWYU aspect:
    ```starlark
    load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

    your_dwyu_aspect = dwyu_aspect_factory(<aspect_options>)
    ```

    Args:
        ignored_includes: By default, DWYU ignores all headers from the standard library when comparing include statements to the dependencies.
                          This list of headers can be seen in [std_header.py](/src/analyze_includes/std_header.py).<br>
                          You can extend this list of ignored headers or replace it with a custom one by providing a json file with the information to this attribute.<br>
                          Specification of possible files in the json file:
                          <ul><li>
                            `ignore_include_paths` : List of include paths which are ignored by the analysis.
                          Setting this **disables ignoring the standard library include paths**.
                          </li><li>
                            `extra_ignore_include_paths` : List of concrete include paths which are ignored by the analysis.
                            Those are always ignored, no matter what other fields you provide.
                          </li><li>
                            `ignore_include_patterns` : List of patterns for include paths which are ignored by the analysis.
                            Patterns have to be compatible to Python [regex syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax).
                            The [match](https://docs.python.org/3/library/re.html#re.match) function is used to process the patterns.
                          </li></ul>
                          This feature is demonstrated in the [ignoring_includes example](/examples/ignoring_includes).
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
        use_implementation_deps: `cc_library` offers the attribute [`implementation_deps`](https://bazel.build/reference/be/c-cpp#cc_library.implementation_deps) to distinguish between public (aka interface) and private (aka implementation) dependencies.
                                 Headers from the private dependencies are not made available to users of the library.<br>
                                 Setting this to True allows DWYU to raise an error if headers from a `deps` dependency are used only in private files.
                                 In such a cease the dependency should be moved from `deps` to `implementation_deps`.<br>
                                 This feature is demonstrated in the [basic_usage example](/examples/basic_usage).
        verbose: If True, print debugging information about what DWYU does.

    Returns:
        Configured DWYU aspect
    """
    attr_aspects = []
    if recursive:
        attr_aspects = ["implementation_deps", "deps"] if use_implementation_deps else ["deps"]
    aspect_ignored_includes = [ignored_includes] if ignored_includes else []
    aspect_skipped_tags = _DEFAULT_SKIPPED_TAGS if skipped_tags == _DEFAULT_SKIPPED_TAGS else skipped_tags
    aspect_target_mapping = [target_mapping] if target_mapping else []
    return aspect(
        implementation = dwyu_aspect_impl,
        attr_aspects = attr_aspects,
        fragments = ["cpp"],
        # Uncomment when minimum Bazel version is 7.0.0, see https://github.com/bazelbuild/bazel/issues/19609
        # DWYU is only able to work on targets providing CcInfo. Other targets shall be skipped.
        # required_providers = [CcInfo],
        toolchains = ["@bazel_tools//tools/cpp:toolchain_type"],
        attrs = {
            "_cc_toolchain": attr.label(
                default = Label("@bazel_tools//tools/cpp:current_cc_toolchain"),
            ),
            "_dwyu_binary": attr.label(
                default = Label("@depend_on_what_you_use//src/analyze_includes:analyze_includes"),
                allow_files = True,
                executable = True,
                cfg = "exec",
                doc = "Tool Analyzing the include statement in the source code under inspection" +
                      " and comparing them to the available dependencies.",
            ),
            "_ignored_includes": attr.label_list(
                default = aspect_ignored_includes,
                allow_files = [".json"],
            ),
            "_process_target": attr.label(
                default = Label("@depend_on_what_you_use//src/aspect:process_target"),
                executable = True,
                cfg = "exec",
                doc = "Tool for processing the target under inspection and its dependencies. We have to perform this" +
                      " as separate action, since otherwise we can't look into TreeArtifact sources.",
            ),
            "_recursive": attr.bool(
                default = recursive,
            ),
            "_skip_external_targets": attr.bool(
                default = skip_external_targets,
            ),
            "_skipped_tags": attr.string_list(
                default = aspect_skipped_tags,
            ),
            "_target_mapping": attr.label_list(
                providers = [DwyuCcInfoRemappingsInfo],
                default = aspect_target_mapping,
            ),
            "_use_implementation_deps": attr.bool(
                default = use_implementation_deps,
            ),
            "_verbose": attr.bool(
                default = verbose,
            ),
        },
    )
