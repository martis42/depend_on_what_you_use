<!-- Generated with Stardoc: http://skydoc.bazel.build -->



<a id="dwyu_aspect_factory"></a>

## dwyu_aspect_factory

<pre>
load("@depend_on_what_you_use//dwyu/aspect:factory.bzl", "dwyu_aspect_factory")

dwyu_aspect_factory(<a href="#dwyu_aspect_factory-analysis_optimizes_impl_deps">analysis_optimizes_impl_deps</a>, <a href="#dwyu_aspect_factory-analysis_reports_missing_direct_deps">analysis_reports_missing_direct_deps</a>,
                    <a href="#dwyu_aspect_factory-analysis_reports_unused_deps">analysis_reports_unused_deps</a>, <a href="#dwyu_aspect_factory-ignored_includes">ignored_includes</a>, <a href="#dwyu_aspect_factory-no_preprocessor">no_preprocessor</a>, <a href="#dwyu_aspect_factory-recursive">recursive</a>,
                    <a href="#dwyu_aspect_factory-enable_with_layering_check">enable_with_layering_check</a>, <a href="#dwyu_aspect_factory-skip_external_targets">skip_external_targets</a>, <a href="#dwyu_aspect_factory-skipped_tags">skipped_tags</a>, <a href="#dwyu_aspect_factory-target_mapping">target_mapping</a>,
                    <a href="#dwyu_aspect_factory-verbose">verbose</a>)
</pre>

Create a "**D**epend on **W**hat **Y**ou **U**se" (DWYU) aspect.

Use the factory in a `.bzl` file to instantiate a DWYU aspect:
```starlark
load("@depend_on_what_you_use//:defs.bzl", "dwyu_aspect_factory")

your_dwyu_aspect = dwyu_aspect_factory(<aspect_options>)
```


**PARAMETERS**


| Name  | Description | Default Value |
| :------------- | :------------- | :------------- |
| <a id="dwyu_aspect_factory-analysis_optimizes_impl_deps"></a>analysis_optimizes_impl_deps |  Setting this to `True` will raise an error for `cc_library` targets where headers from a `deps` dependency are used only in private files. Such dependencies should be moved from `deps` to [implementation_deps](https://bazel.build/reference/be/c-cpp#cc_library.implementation_deps) to optimize the dependency graph of the project.<br> This flag can also be controlled in a Bazel config or on the command line via `--aspects_parameters=dwyu_analysis_optimizes_impl_deps=[True\|False]`.<br> This feature is demonstrated in the [basic_usage example](/examples/basic_usage).   |  `False` |
| <a id="dwyu_aspect_factory-analysis_reports_missing_direct_deps"></a>analysis_reports_missing_direct_deps |  Setting this to `True` will report include statements in the files of the target under inspection which are not covered by any of the direct dependencies of the target. This is useful to identify missing dependencies in the dependency graph of the project.<br> This flag can also be controlled in a Bazel config or on the command line via `--aspects_parameters=dwyu_analysis_reports_missing_direct_deps=[True\|False]`.   |  `True` |
| <a id="dwyu_aspect_factory-analysis_reports_unused_deps"></a>analysis_reports_unused_deps |  Setting this to `True` will report dependencies which are not used in any of the files of the target under inspection as unused. This is useful to identify dependencies which can be removed from the dependency graph of the project.<br> This flag is only supported by the C++ based implementation of DWYU.<br> This flag can also be controlled in a Bazel config or on the command line via `--aspects_parameters=dwyu_analysis_reports_unused_deps=[True\|False]`   |  `True` |
| <a id="dwyu_aspect_factory-ignored_includes"></a>ignored_includes |  The DWYU analysis ignores all files which are provided by the Bazel CC toolchain (e.g. the standard library headers). If you want to ignore additional headers, you can provide a json file with the information to this attribute.<br> The ignore logic works on the path provided to the include statement, e.g. `#include <foo/bar.h>` will be checked against the ignore list as `foo/bar.h`.<br> Json file specification: <ul><li>   `ignore_include_paths` : List of include paths which are ignored by the analysis. </li><li>   `ignore_include_patterns` : List of patterns which are ignored by the analysis.   The [boost regex library](https://www.boost.org/doc/libs/latest/libs/regex/doc/html/index.html) is used to parse the patterns.   The [boost::regex_search](https://www.boost.org/doc/libs/latest/libs/regex/doc/html/boost_regex/ref/regex_search.html) function is used to compare the patterns to the include statements. </li></ul> This feature is demonstrated in the [ignoring_includes example](/examples/ignoring_includes).   |  `None` |
| <a id="dwyu_aspect_factory-no_preprocessor"></a>no_preprocessor |  This option disables the preprocessing step before discovering the include statements in the files under inspection. When the preprocessing is disabled, DWYU still ignores commented include statements. Using this option can speed up the DWYU analysis.<br> When using this option, DWYU will no longer be able to correctly resolve conditional include logic (`#ifdef` around include statements) or any other preprocessor directives and macros influencing include statements. A common example requiring preprocessing is having different include statements and Bazel target dependencies depending on whether the host is a Windows or Linux system.   |  `False` |
| <a id="dwyu_aspect_factory-recursive"></a>recursive |  By default, the DWYU aspect analyzes only the target it is being applied to. You can change this to recursively analyzing dependencies following the `deps` and `implementation_deps` attributes by setting this to True.<br> This feature is demonstrated in the [recursion example](/examples/recursion).   |  `False` |
| <a id="dwyu_aspect_factory-enable_with_layering_check"></a>enable_with_layering_check |  If `True`, DWYU will only analyze targets for which the `layering_check` C++ toolchain feature is enabled (as determined by `cc_common.is_enabled`). This allows opting individual targets or packages in or out of DWYU via the standard `features` attribute, e.g. `features = ["layering_check"]` to opt in or `features = ["-layering_check"]` to opt out. By default this gating is disabled and DWYU analyzes all matching targets.   |  `False` |
| <a id="dwyu_aspect_factory-skip_external_targets"></a>skip_external_targets |  Sometimes external dependencies are not our under control and thus analyzing them is of little value. If this flag is True, DWYU will automatically skip all targets from external workspaces. This can be useful in combination with the recursive analysis mode.<br> This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).   |  `False` |
| <a id="dwyu_aspect_factory-skipped_tags"></a>skipped_tags |  Do not execute the DWYU analysis on targets with at least one of those tags. By default skips the analysis for targets tagged with 'no-dwyu'.<br> This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).   |  `["no-dwyu"]` |
| <a id="dwyu_aspect_factory-target_mapping"></a>target_mapping |  Accepts a [dwyu_make_cc_info_mapping](/docs/cc_info_mapping.md) target. Allows virtually combining targets regarding which header can be provided by which dependency. For the full details see the `dwyu_make_cc_info_mapping` documentation.<br> This feature is demonstrated in the [target_mapping example](/examples/target_mapping).   |  `None` |
| <a id="dwyu_aspect_factory-verbose"></a>verbose |  If `True`, print debugging information about the individual DWYU actions.<br> This flag can also be controlled in a Bazel config or on the command line via `--aspects_parameters=dwyu_verbose=[True\|False]`.   |  `False` |

**RETURNS**

Configured DWYU aspect


