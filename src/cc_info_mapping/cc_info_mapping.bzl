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
Then a test can specify only the dependency to `@com_google_googletest//:gtest_main` without DWYU raising an error while analysing the test.
"""

load("//src/cc_info_mapping/private:direct_deps.bzl", "mapping_to_direct_deps")
load("//src/cc_info_mapping/private:explicit.bzl", "explicit_mapping")
load("//src/cc_info_mapping/private:providers.bzl", "DwyuRemappedCcInfo")
load("//src/cc_info_mapping/private:transitive_deps.bzl", "mapping_to_transitive_deps")
load("//src/private:utils.bzl", "label_to_name")
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

def dwyu_make_cc_info_mapping(name, mapping):
    """
    Map include paths available from one or several targets to another target.

    Create a mapping allowing treating targets as if they themselves would offer header files, which in fact are coming from their dependencies.
    This enables the DWYU analysis to skip over some usage of headers provided by transitive dependencies without raising an error.

    Using this rule and the various mapping techniques is demonstrated in the [target_mapping example](/examples/target_mapping).

    Args:
        name: Unique name for this target. Will be the prefix for all private intermediate targets.
        mapping: Dictionary containing various targets and how they should be mapped. Possible mappings are:<br>
                 - An explicit list of targets which are mapped to the main target.
                   Be careful only to choose targets which are dependencies of the main target! <br>
                 - The `MAP_DIRECT_DEPS` token which tells the rule to map all direct dependencies to the main target. <br>
                 - The `MAP_TRANSITIVE_DEPS` token which tells the rule to map recursively all transitive dependencies to the main target.
    """
    mappings = []
    for target, map_to in mapping.items():
        mapping_action = "{}_mapping_{}".format(name, label_to_name(target))
        if map_to == MAP_DIRECT_DEPS:
            mapping_to_direct_deps(
                name = mapping_action,
                target = target,
            )
        elif map_to == MAP_TRANSITIVE_DEPS:
            mapping_to_transitive_deps(
                name = mapping_action,
                target = target,
            )
        else:
            explicit_mapping(
                name = mapping_action,
                target = target,
                map_to = map_to,
            )
        mappings.append(mapping_action)

    _make_remapping_info(
        name = name,
        remappings = mappings,
    )
