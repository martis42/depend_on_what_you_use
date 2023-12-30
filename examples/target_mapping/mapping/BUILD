load("@depend_on_what_you_use//:defs.bzl", "MAP_DIRECT_DEPS", "MAP_TRANSITIVE_DEPS", "dwyu_make_cc_info_mapping")

package(default_visibility = ["//target_mapping:__pkg__"])

dwyu_make_cc_info_mapping(
    name = "map_specific_deps",
    mapping = {
        "//target_mapping/libs:a": ["//target_mapping/libs:b"],
    },
)

dwyu_make_cc_info_mapping(
    name = "map_direct_deps",
    mapping = {
        "//target_mapping/libs:a": MAP_DIRECT_DEPS,
    },
)

dwyu_make_cc_info_mapping(
    name = "map_transitive_deps",
    mapping = {
        "//target_mapping/libs:a": MAP_TRANSITIVE_DEPS,
    },
)
