<!-- Generated with Stardoc: http://skydoc.bazel.build -->

Sometimes users don't want to follow the DWYU rules for all targets or have to work with external dependencies not following the DWYU principles.
While one can exclude targets from the DWYU analysis completely (e.g. via tags), one can also explicitly define exceptions where includes can be provided by selected transitive dependencies instead of direct dependencies.
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
Then a test can specify only the dependency to `@com_google_googletest//:gtest_main` without DWYU raising an error while analysing the test.

<a id="DwyuCcInfoRemappingsInfo"></a>

## DwyuCcInfoRemappingsInfo

<pre>
DwyuCcInfoRemappingsInfo(<a href="#DwyuCcInfoRemappingsInfo-mapping">mapping</a>)
</pre>

Mapping of targets to CcInfo providers which DWYU should use for analyis instead of the targets original CcInfo.

**FIELDS**


| Name  | Description |
| :------------- | :------------- |
| <a id="DwyuCcInfoRemappingsInfo-mapping"></a>mapping |  Dictionary with structure {'target label': CcInfo}    |


<a id="dwyu_make_cc_info_mapping"></a>

## dwyu_make_cc_info_mapping

<pre>
dwyu_make_cc_info_mapping(<a href="#dwyu_make_cc_info_mapping-name">name</a>, <a href="#dwyu_make_cc_info_mapping-mapping">mapping</a>)
</pre>

Map include paths available from one or several targets to another target.

Create a mapping which allows treating targets as if they themselves would offer header files, which in fact are
coming from their dependencies. This enables the DWYU analysis to skip over some usage of headers provided by
transitive dependencies without raising an error.


**PARAMETERS**


| Name  | Description | Default Value |
| :------------- | :------------- | :------------- |
| <a id="dwyu_make_cc_info_mapping-name"></a>name |  Unique name for this target. Will be the prefix for all private intermediate targets.   |  none |
| <a id="dwyu_make_cc_info_mapping-mapping"></a>mapping |  Dictionary containing various targets and how they should be mapped. Possible mappings are: - An explicit list of targets which are mapped to the main target. Be careful only to choose targets   which are dependencies of the main target! - The MAP_DIRECT_DEPS token which tells the rule to map all direct dependencies to the main target. - The MAP_TRANSITIVE_DEPS token which tells the rule to map recursively all transitive dependencies to   the main target.   |  none |


