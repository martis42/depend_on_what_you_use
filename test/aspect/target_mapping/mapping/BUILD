load("@depend_on_what_you_use//dwyu/cc:defs.bzl", "MAP_DIRECT_DEPS", "MAP_TRANSITIVE_DEPS", "dwyu_make_cc_info_mapping")
load(":to_canonical.bzl", "to_canonical")

package(default_visibility = ["//target_mapping:__pkg__"])

dwyu_make_cc_info_mapping(
    name = "map_specific_deps",
    mapping = {
        "//target_mapping/libs:a": ["//target_mapping/libs:b"],
    },
)

# Legacy syntax: a plain MAP_DIRECT_DEPS/MAP_TRANSITIVE_DEPS token always maps all direct/transitive deps, filtering is not supported.
dwyu_make_cc_info_mapping(
    name = "map_direct_deps_legacy",
    mapping = {
        "//target_mapping/libs:a": MAP_DIRECT_DEPS,
    },
)

dwyu_make_cc_info_mapping(
    name = "map_transitive_deps_legacy",
    mapping = {
        "//target_mapping/libs:a": MAP_TRANSITIVE_DEPS,
    },
)

# New syntax mapping all direct/transitive deps, equivalent to the legacy behavior above.
dwyu_make_cc_info_mapping(
    name = "map_direct_deps_all",
    mapping = {
        "//target_mapping/libs:a": {MAP_DIRECT_DEPS: "all"},
    },
)

dwyu_make_cc_info_mapping(
    name = "map_transitive_deps_all",
    mapping = {
        "//target_mapping/libs:a": {MAP_TRANSITIVE_DEPS: "all"},
    },
)

# New syntax filtering to only the canonical target names for which headers shall be mapped, including a target from an external repo.
dwyu_make_cc_info_mapping(
    name = "map_direct_deps_filtered",
    mapping = {
        "//target_mapping/libs:with_external_dep": {MAP_DIRECT_DEPS: [to_canonical("@target_mapping_test_repo//:ext")]},
    },
)

dwyu_make_cc_info_mapping(
    name = "map_transitive_deps_filtered",
    mapping = {
        "//target_mapping/libs:with_external_dep": {MAP_TRANSITIVE_DEPS: [to_canonical("@target_mapping_test_repo//:ext")]},
    },
)
