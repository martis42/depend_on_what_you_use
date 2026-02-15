<!-- Generated with Stardoc: http://skydoc.bazel.build -->



<a id="dwyu_aspect_factory"></a>

## dwyu_aspect_factory

<pre>
load("@depend_on_what_you_use//dwyu/aspect:factory.bzl", "dwyu_aspect_factory")

dwyu_aspect_factory(<a href="#dwyu_aspect_factory-analysis_optimizes_impl_deps">analysis_optimizes_impl_deps</a>, <a href="#dwyu_aspect_factory-analysis_reports_missing_direct_deps">analysis_reports_missing_direct_deps</a>,
                    <a href="#dwyu_aspect_factory-analysis_reports_unused_deps">analysis_reports_unused_deps</a>, <a href="#dwyu_aspect_factory-experimental_no_preprocessor">experimental_no_preprocessor</a>,
                    <a href="#dwyu_aspect_factory-experimental_set_cplusplus">experimental_set_cplusplus</a>, <a href="#dwyu_aspect_factory-ignored_includes">ignored_includes</a>, <a href="#dwyu_aspect_factory-no_preprocessor">no_preprocessor</a>, <a href="#dwyu_aspect_factory-recursive">recursive</a>,
                    <a href="#dwyu_aspect_factory-skip_external_targets">skip_external_targets</a>, <a href="#dwyu_aspect_factory-skipped_tags">skipped_tags</a>, <a href="#dwyu_aspect_factory-target_mapping">target_mapping</a>, <a href="#dwyu_aspect_factory-use_cpp_implementation">use_cpp_implementation</a>,
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
| <a id="dwyu_aspect_factory-experimental_no_preprocessor"></a>experimental_no_preprocessor |  Deprecated flag. This feature is now stable. See [no_preprocessor](https://github.com/martis42/depend_on_what_you_use/blob/main/docs/dwyu_aspect.md#dwyu_aspect_factory-no_preprocessor)   |  `False` |
| <a id="dwyu_aspect_factory-experimental_set_cplusplus"></a>experimental_set_cplusplus |  **DEPRECATED**: This flag will be removed together with the Python implementation. The new C++ based implementation will always try to set a proper `__cplusplus`.<br><br> `__cplusplus` is a macro defined by the compiler specifying if C++ is used to compile the file and which C++ standard is used.<br> DWYU cannot treat this like other preprocessor defines, as this is often not coming from the command line or the Bazel C++ toolchain. The compiler itself defines the value for `__cplusplus` and sets it internally during preprocessing.<br> This option enables a heuristic to set `__cplusplus` for the preprocessor used internally by DWYU. We look at the compilation command one would use to compile the code and look for `-std=..`. If it is is present and has a legal value, we deduce `__cplusplus` and set it for the preprocessing. If this logic fails, `__cplusplus` is not set. Users can provide their own value by setting `__cplusplus` via Bazel (e.g. via `--cxxopt=-D__cplusplus=42`) which will take precedence over the heuristic used by DWYU. This feature is demonstrated in the [set_cpp_standard example](/examples/set_cpp_standard).   |  `False` |
| <a id="dwyu_aspect_factory-ignored_includes"></a>ignored_includes |  By default, DWYU ignores all headers from the standard library when comparing include statements to the dependencies. This list of headers can be seen in [std_header.py](/dwyu/aspect/private/analyze_includes/std_header.py).<br> You can extend this list of ignored headers or replace it with a custom one by providing a json file with the information to this attribute.<br> Specification of possible files in the json file: <ul><li>   `ignore_include_paths` : List of include paths which are ignored by the analysis.   Setting this **disables ignoring the system and standard library include paths**. </li><li>   `extra_ignore_include_paths` : List of concrete include paths which are ignored by the analysis.   Those are always ignored, no matter what other fields you provide. </li><li>   `ignore_include_patterns` : List of patterns for include paths which are ignored by the analysis.   Patterns have to be compatible to Python [regex syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax).   The [match](https://docs.python.org/3/library/re.html#re.match) function is used to process the patterns. </li></ul> This feature is demonstrated in the [ignoring_includes example](/examples/ignoring_includes).   |  `None` |
| <a id="dwyu_aspect_factory-no_preprocessor"></a>no_preprocessor |  This option disables the preprocessing step before discovering the include statements in the files under inspection. When the preprocessing is disabled, DWYU still ignores commented include statements. Using this option can speed up the DWYU analysis.<br> When using this option, DWYU will no longer be able to correctly resolve conditional include logic (`#ifdef` around include statements) or any other preprocessor directives and macros influencing include statements. A common example requiring preprocessing is having different include statements and Bazel target dependencies depending on whether the host is a Windows or Linux system.   |  `False` |
| <a id="dwyu_aspect_factory-recursive"></a>recursive |  By default, the DWYU aspect analyzes only the target it is being applied to. You can change this to recursively analyzing dependencies following the `deps` and `implementation_deps` attributes by setting this to True.<br> This feature is demonstrated in the [recursion example](/examples/recursion).   |  `False` |
| <a id="dwyu_aspect_factory-skip_external_targets"></a>skip_external_targets |  Sometimes external dependencies are not our under control and thus analyzing them is of little value. If this flag is True, DWYU will automatically skip all targets from external workspaces. This can be useful in combination with the recursive analysis mode.<br> This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).   |  `False` |
| <a id="dwyu_aspect_factory-skipped_tags"></a>skipped_tags |  Do not execute the DWYU analysis on targets with at least one of those tags. By default skips the analysis for targets tagged with 'no-dwyu'.<br> This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).   |  `["no-dwyu"]` |
| <a id="dwyu_aspect_factory-target_mapping"></a>target_mapping |  Accepts a [dwyu_make_cc_info_mapping](/docs/cc_info_mapping.md) target. Allows virtually combining targets regarding which header can be provided by which dependency. For the full details see the `dwyu_make_cc_info_mapping` documentation.<br> This feature is demonstrated in the [target_mapping example](/examples/target_mapping).   |  `None` |
| <a id="dwyu_aspect_factory-use_cpp_implementation"></a>use_cpp_implementation |  Set this to `False` to use the legacy Python based implementation. If you have to use the Python implementation instead of the standard C++ based implementation, please create an issue with your problem in the [DWYU issue tracker](https://github.com/martis42/depend_on_what_you_use/issues).<br> **The Python based implementation will be removed in a future release**!   |  `True` |
| <a id="dwyu_aspect_factory-verbose"></a>verbose |  If `True`, print debugging information about the individual DWYU actions.<br> This flag can also be controlled in a Bazel config or on the command line via `--aspects_parameters=dwyu_verbose=[True\|False]`.   |  `False` |

**RETURNS**

Configured DWYU aspect


