<!-- Generated with Stardoc: http://skydoc.bazel.build -->

# Motivation

Sometimes users don't want to follow the DWYU rules for all targets or have to work with external dependencies not following the DWYU principles.
While one can completely exclude targets from the DWYU analysis (e.g. via tags), one might not want to disable DWYU completely, but define custom rules for specific dependencies.
One can do so by defining exceptions where includes can be provided by selected transitive dependencies instead of direct dependencies.
In other words, one can virtually change which header files are treated as being available from direct dependencies.

One example use case for this are unit tests based on gtest.
Following strictly the DWYU principles each test using a gtest header should depend both on the gtest library and the gtest main:
```starlark
cc_test(
  name = "my_test",
  srcs = ["my_test.cc"],
  deps = [
    "@com_google_googletest//:gtest",
    "@com_google_googletest//:gtest_main",
  ],
)
```
This can be considered superfluous noise without a significant benefit.
The mapping feature described here allows defining that `@com_google_googletest//:gtest_main` offers the header files from `@com_google_googletest//:gtest`.
Then a test can specify only the dependency to `@com_google_googletest//:gtest_main` without DWYU raising an error while analyzing the test.

<a id="dwyu_make_cc_info_mapping"></a>

## dwyu_make_cc_info_mapping

<pre>
load("@depend_on_what_you_use//dwyu/cc/cc_info_mapping:cc_info_mapping.bzl", "dwyu_make_cc_info_mapping")

dwyu_make_cc_info_mapping(<a href="#dwyu_make_cc_info_mapping-name">name</a>, <a href="#dwyu_make_cc_info_mapping-mapping">mapping</a>)
</pre>

Map include paths available from one or several targets to another target.

Create a mapping allowing treating targets as if they themselves would offer header files, which in fact are coming from their dependencies.
This enables the DWYU analysis to skip over some usage of headers provided by transitive dependencies without raising an error.

Example usage:

```starlark
dwyu_make_cc_info_mapping(
    name = "my_mapping",
    mapping = {
        "//target/mapped/to/some/direct:dependencies": {
            MAP_DIRECT_DEPS: ["@@//direct/dependency:foo", "@@external//direct/dependency:bar"],
        },
        "//target/mapped/to/all/transitive:dependencies": {
            MAP_TRANSITIVE_DEPS: "all",
        },
        "//target/mapped/to/specific:targets": {
            MAP_EXPLICIT_DEPS: ["@@//other:target"]
        },
    },
)
```

When using filtering, we recommend using a helper macro, like `def to_canonical(target): return str(Label(target))`, instead of hard coding canonical target names.
Using this rule and the various mapping techniques is demonstrated in the [target_mapping example](/examples/target_mapping).


**PARAMETERS**


| Name  | Description | Default Value |
| :------------- | :------------- | :------------- |
| <a id="dwyu_make_cc_info_mapping-name"></a>name |  Unique name for this target. Will be the prefix for all private intermediate targets.   |  none |
| <a id="dwyu_make_cc_info_mapping-mapping"></a>mapping |  Dictionary containing various targets and how they should be mapped. Possible mappings are:<br> - The `MAP_DIRECT_DEPS` mode tells the rule to map direct dependencies to the main target.   Choose `all` to automatically map all direct dependencies.   Provide a list of strings with canonical target names to limit the mapping to a subset of direct dependencies.   Using `MAP_DIRECT_DEPS` as single value without providing `all` or a filter list is the legacy behavior falling back to mapping all direct dependencies.   This legacy behavior will be removed in a future release.<br> - The `MAP_TRANSITIVE_DEPS` mode tells the rule to map direct dependencies including their transitive dependencies to the main target.   Choose `all` to automatically map all dependencies.   Provide a list of strings with canonical target names to limit the mapping to a subset of direct dependencies for which the transitive dependencies are mapped as well.   Meaning, only direct dependencies are valid entries in the filter list.   Using `MAP_TRANSITIVE_DEPS` as single value without providing `all` or a filter list is the legacy behavior falling back to mapping all dependencies.   This legacy behavior will be removed in a future release.<br> - The `MAP_EXPLICIT_DEPS` mode tells the rule to map a list of CcInfo-providing targets to the main target.   The list has to use the canonical target names and the targets have to be from the dependency tree of the main target.   For this mapping rule, the dependency tree is not just defined by the `deps` attribute of the rules_cc rules.   All rules with all attributes providing CcInfo-providing targets are traversed.</br> - An explicit list of targets which are mapped to the main target.   This is a legacy behavior which will be removed eventually.   Use `MAP_EXPLICIT_DEPS` instead.</br>   |  none |


