"""
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
"""

load("//dwyu/cc/cc_info_mapping/private:direct_deps.bzl", "mapping_to_direct_deps")
load("//dwyu/cc/cc_info_mapping/private:explicit.bzl", "explicit_mapping")
load("//dwyu/cc/cc_info_mapping/private:providers.bzl", "DwyuRemappedCcInfo")
load("//dwyu/cc/cc_info_mapping/private:transitive_deps.bzl", "mapping_to_transitive_deps")
load("//dwyu/private:utils.bzl", "label_to_name")
load(":providers.bzl", "DwyuCcInfoMappingInfo")

MAP_DIRECT_DEPS = "__DWYU_MAP_DIRECT_DEPS__"
MAP_TRANSITIVE_DEPS = "__DWYU_MAP_TRANSITIVE_DEPS__"

def _make_remapping_info_impl(ctx):
    return DwyuCcInfoMappingInfo(mapping = {
        remap[DwyuRemappedCcInfo].target: remap[DwyuRemappedCcInfo].cc_info
        for remap in ctx.attr.remappings
    })

_make_remapping_info = rule(
    implementation = _make_remapping_info_impl,
    provides = [DwyuCcInfoMappingInfo],
    attrs = {
        "remappings": attr.label_list(providers = [DwyuRemappedCcInfo]),
    },
)

def _extract_mapping_value(map, key):
    value = map[key]
    if type(value) == "string" and value.lower() == "all":
        return []
    elif type(value) == "list":
        return value
    return None

def dwyu_make_cc_info_mapping(name, mapping):
    """
    Map include paths available from one or several targets to another target.

    Create a mapping allowing treating targets as if they themselves would offer header files, which in fact are coming from their dependencies.
    This enables the DWYU analysis to skip over some usage of headers provided by transitive dependencies without raising an error.

    Example usage:

    ```starlark
    dwyu_make_cc_info_mapping(
        name = "my_mapping",
        mapping = {
            "//target/mapped/to/specific:targets": ["//other/target"],
            "//target/mapped/to/some/direct:dependencies": {
                MAP_DIRECT_DEPS: ["//direct/dependency:foo", "//direct/dependency:bar"],
            },
            "//target/mapped/to/all/direct:dependencies": {
                MAP_TRANSITIVE_DEPS: "all",
            },
        },
    )
    ```

    Using this rule and the various mapping techniques is demonstrated in the [target_mapping example](/examples/target_mapping).

    Args:
        name: Unique name for this target. Will be the prefix for all private intermediate targets.
        mapping: Dictionary containing various targets and how they should be mapped. Possible mappings are:<br>
                 - An explicit list of targets which are mapped to the main target.
                   Be careful only to choose targets which are dependencies of the main target!
                   If you can't use this due to visibility restrictions, consider using the `MAP_DIRECT_DEPS` mode instead with appropriate target filters.<br>
                 - The `MAP_DIRECT_DEPS` mode tells the rule to map direct dependencies to the main target.
                   Choose `all` to automatically map all direct dependencies.
                   Provide a list of strings with canonical target names to limit the mapping to a subset of direct dependencies.
                   Using `MAP_DIRECT_DEPS` as single value without providing `all` or a filter list is the legacy behavior falling back to mapping all direct dependencies.
                   This legacy behavior will be removed in a future release.<br>
                 - The `MAP_TRANSITIVE_DEPS` mode tells the rule to map direct and transitive dependencies to the main target.
                   Choose `all` to automatically map all dependencies.
                   Provide a list of strings with canonical target names to limit the mapping to a subset of direct dependencies for which the transitive dependencies are mapped as well.
                   Meaning, only direct dependencies are valid entries in the filter list.
                   Using `MAP_TRANSITIVE_DEPS` as single value without providing `all` or a filter list is the legacy behavior falling back to mapping all dependencies.
                   This legacy behavior will be removed in a future release.<br>
    """
    mappings = []
    for target, map_to in mapping.items():
        mapping_action = "{}_mapping_{}".format(name, label_to_name(target))
        if type(map_to) == "list":
            explicit_mapping(
                name = mapping_action,
                target = target,
                map_to = map_to,
            )
        elif type(map_to) == "string":
            # Legacy cases falling back to 'map all deps'
            if map_to == MAP_DIRECT_DEPS:
                mapping_to_direct_deps(
                    name = mapping_action,
                    target = target,
                    filter = [],
                )
            elif map_to == MAP_TRANSITIVE_DEPS:
                mapping_to_transitive_deps(
                    name = mapping_action,
                    target = target,
                    filter = [],
                )
            else:
                fail("DWYU: Invalid mapping value for target {}: {}".format(target, map_to))
        elif type(map_to) == "dict":
            if [MAP_DIRECT_DEPS] == map_to.keys():
                filter = _extract_mapping_value(map_to, MAP_DIRECT_DEPS)
                if filter == None:
                    fail("DWYU: Invalid mapping value for target {}: {}".format(target, map_to))
                mapping_to_direct_deps(
                    name = mapping_action,
                    target = target,
                    filter = filter,
                )
            elif [MAP_TRANSITIVE_DEPS] == map_to.keys():
                filter = _extract_mapping_value(map_to, MAP_TRANSITIVE_DEPS)
                if filter == None:
                    fail("DWYU: Invalid mapping value for target {}: {}".format(target, map_to))
                mapping_to_transitive_deps(
                    name = mapping_action,
                    target = target,
                    filter = filter,
                )
            else:
                fail("DWYU: Invalid mapping value for target {}: {}".format(target, map_to))
        else:
            fail("DWYU: Invalid mapping value for target {}: {}".format(target, map_to))
        mappings.append(mapping_action)

    _make_remapping_info(
        name = name,
        remappings = mappings,
    )
