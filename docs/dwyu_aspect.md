<!-- Generated with Stardoc: http://skydoc.bazel.build -->



<a id="dwyu_aspect_factory"></a>

## dwyu_aspect_factory

<pre>
load("@depend_on_what_you_use//src/aspect:factory.bzl", "dwyu_aspect_factory")

dwyu_aspect_factory(<a href="#dwyu_aspect_factory-experimental_set_cplusplus">experimental_set_cplusplus</a>, <a href="#dwyu_aspect_factory-ignored_includes">ignored_includes</a>, <a href="#dwyu_aspect_factory-recursive">recursive</a>, <a href="#dwyu_aspect_factory-skip_external_targets">skip_external_targets</a>,
                    <a href="#dwyu_aspect_factory-skipped_tags">skipped_tags</a>, <a href="#dwyu_aspect_factory-target_mapping">target_mapping</a>, <a href="#dwyu_aspect_factory-use_implementation_deps">use_implementation_deps</a>, <a href="#dwyu_aspect_factory-verbose">verbose</a>)
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
| <a id="dwyu_aspect_factory-experimental_set_cplusplus"></a>experimental_set_cplusplus |  **Experimental** feature whose behavior is not yet stable and an change at any time.<br> `__cplusplus` is a macro defined by the compiler specifying if C++ is used to compile the file and which C++ standard is used.<br> DWYU cannot treat this like other preprocessor defines, as this is often not coming from the command line or the Bazel C++ toolchain. The compiler itself defines the value for `__cplusplus` and sets it internally during preprocessing.<br> This option enables a heuristic to set `__cplusplus` for the preprocessor used internally by DWYU: <ul><li>   If at least one source file is not using file extension [`.c`, `.h`], set `__cplusplus` to 1. </li><li>   If a common compiler option is used to set the C++ standard with an unknown value, set `__cplusplus` to 1. </li><li>   If a common compiler option is used to set the C++ standard with an known value, set `__cplusplus` according to [this map](https://en.cppreference.com/w/cpp/preprocessor/replace#Predefined_macros). </li></ul> This feature is demonstrated in the [set_cpp_standard example](/examples/set_cpp_standard).   |  `False` |
| <a id="dwyu_aspect_factory-ignored_includes"></a>ignored_includes |  By default, DWYU ignores all headers from the standard library when comparing include statements to the dependencies. This list of headers can be seen in [std_header.py](/src/analyze_includes/std_header.py).<br> You can extend this list of ignored headers or replace it with a custom one by providing a json file with the information to this attribute.<br> Specification of possible files in the json file: <ul><li>   `ignore_include_paths` : List of include paths which are ignored by the analysis.   Setting this **disables ignoring the standard library include paths**. </li><li>   `extra_ignore_include_paths` : List of concrete include paths which are ignored by the analysis.   Those are always ignored, no matter what other fields you provide. </li><li>   `ignore_include_patterns` : List of patterns for include paths which are ignored by the analysis.   Patterns have to be compatible to Python [regex syntax](https://docs.python.org/3/library/re.html#regular-expression-syntax).   The [match](https://docs.python.org/3/library/re.html#re.match) function is used to process the patterns. </li></ul> This feature is demonstrated in the [ignoring_includes example](/examples/ignoring_includes).   |  `None` |
| <a id="dwyu_aspect_factory-recursive"></a>recursive |  By default, the DWYU aspect analyzes only the target it is being applied to. You can change this to recursively analyzing dependencies following the `deps` and `implementation_deps` attributes by setting this to True.<br> This feature is demonstrated in the [recursion example](/examples/recursion).   |  `False` |
| <a id="dwyu_aspect_factory-skip_external_targets"></a>skip_external_targets |  Sometimes external dependencies are not our under control and thus analyzing them is of little value. If this flag is True, DWYU will automatically skip all targets from external workspaces. This can be useful in combination with the recursive analysis mode.<br> This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).   |  `False` |
| <a id="dwyu_aspect_factory-skipped_tags"></a>skipped_tags |  Do not execute the DWYU analysis on targets with at least one of those tags. By default skips the analysis for targets tagged with 'no-dwyu'.<br> This feature is demonstrated in the [skipping_targets example](/examples/skipping_targets).   |  `["no-dwyu"]` |
| <a id="dwyu_aspect_factory-target_mapping"></a>target_mapping |  Accepts a [dwyu_make_cc_info_mapping](/docs/cc_info_mapping.md) target. Allows virtually combining targets regarding which header can be provided by which dependency. For the full details see the `dwyu_make_cc_info_mapping` documentation.<br> This feature is demonstrated in the [target_mapping example](/examples/target_mapping).   |  `None` |
| <a id="dwyu_aspect_factory-use_implementation_deps"></a>use_implementation_deps |  `cc_library` offers the attribute [`implementation_deps`](https://bazel.build/reference/be/c-cpp#cc_library.implementation_deps) to distinguish between public (aka interface) and private (aka implementation) dependencies. Headers from the private dependencies are not made available to users of the library.<br> Setting this to True allows DWYU to raise an error if headers from a `deps` dependency are used only in private files. In such a cease the dependency should be moved from `deps` to `implementation_deps`.<br> This feature is demonstrated in the [basic_usage example](/examples/basic_usage).   |  `False` |
| <a id="dwyu_aspect_factory-verbose"></a>verbose |  If True, print debugging information about what DWYU does.   |  `False` |

**RETURNS**

Configured DWYU aspect


