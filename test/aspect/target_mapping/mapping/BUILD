load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "MAP_DIRECT_DEPS", "MAP_TRANSITIVE_DEPS", "dwyu_make_cc_info_mapping")
load(":to_canonical.bzl", "to_canonical")

package(default_visibility = ["//target_mapping:__pkg__"])

dwyu_make_cc_info_mapping(
    name = "map_specific_deps",
    mapping = {
        "//target_mapping/libs:mapped_dep": [
            "//target_mapping/libs:a",
            "@target_mapping_test_repo//:ext_a",
        ],
    },
)

# Legacy syntax: A plain MAP_DIRECT_DEPS token always maps all direct deps, filtering is not supported.
dwyu_make_cc_info_mapping(
    name = "map_direct_deps_legacy",
    mapping = {
        "//target_mapping/libs:mapped_dep": MAP_DIRECT_DEPS,
    },
)

# Legacy syntax: A plain MAP_TRANSITIVE_DEPS token always maps all transitive deps, filtering is not supported.
dwyu_make_cc_info_mapping(
    name = "map_transitive_deps_legacy",
    mapping = {
        "//target_mapping/libs:mapped_dep": MAP_TRANSITIVE_DEPS,
    },
)

dwyu_make_cc_info_mapping(
    name = "map_direct_deps_all",
    mapping = {
        "//target_mapping/libs:mapped_dep": {MAP_DIRECT_DEPS: "all"},
    },
)

dwyu_make_cc_info_mapping(
    name = "map_transitive_deps_all",
    mapping = {
        "//target_mapping/libs:mapped_dep": {MAP_TRANSITIVE_DEPS: "all"},
    },
)

dwyu_make_cc_info_mapping(
    name = "map_direct_deps_filtered",
    mapping = {
        "//target_mapping/libs:mapped_dep": {MAP_DIRECT_DEPS: [to_canonical("@target_mapping_test_repo//:ext_a")]},
    },
)

dwyu_make_cc_info_mapping(
    name = "map_transitive_deps_filtered",
    mapping = {
        "//target_mapping/libs:mapped_dep": {MAP_TRANSITIVE_DEPS: [to_canonical("@target_mapping_test_repo//:ext_a")]},
    },
)
