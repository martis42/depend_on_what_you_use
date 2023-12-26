load("//:defs.bzl", "MAP_DIRECT_DEPS", "MAP_TRANSITIVE_DEPS", "dwyu_make_cc_info_mapping")

package(default_visibility = ["//test/aspect/target_mapping:__pkg__"])

dwyu_make_cc_info_mapping(
    name = "map_specific_deps",
    mapping = {
        "//test/aspect/target_mapping/libs:a": ["//test/aspect/target_mapping/libs:b"],
    },
)

dwyu_make_cc_info_mapping(
    name = "map_direct_deps",
    mapping = {
        "//test/aspect/target_mapping/libs:a": MAP_DIRECT_DEPS,
    },
)

dwyu_make_cc_info_mapping(
    name = "map_transitive_deps",
    mapping = {
        "//test/aspect/target_mapping/libs:a": MAP_TRANSITIVE_DEPS,
    },
)
