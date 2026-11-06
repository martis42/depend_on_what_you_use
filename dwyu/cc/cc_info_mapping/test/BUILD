load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("//dwyu/cc/cc_info_mapping:cc_info_mapping.bzl", "MAP_DIRECT_DEPS", "dwyu_make_cc_info_mapping")
load(":aggregation_test.bzl", "aggregation_test_suite")
load(":custom_rules.bzl", "custom_remapping", "invalid_remapping")

aggregation_test_suite(name = "aggregation_tests")

cc_library(
    name = "dep",
    hdrs = ["dep.h"],
)

cc_library(
    name = "lib_with_dep",
    hdrs = ["lib_with_dep.h"],
    deps = [":dep"],
)

cc_library(
    name = "other_lib",
    deps = [":dep"],
)

custom_remapping(
    name = "custom",
    dep = ":dep",
    target = ":lib_with_dep",
)

custom_remapping(
    name = "another_custom",
    dep = ":dep",
    target = ":lib_with_dep",
)

dwyu_make_cc_info_mapping(
    name = "mapping_with_custom_and_builtin",
    custom_remappings = [":custom"],
    mapping = {
        "//dwyu/cc/cc_info_mapping/test:other_lib": {MAP_DIRECT_DEPS: "all"},
    },
)

dwyu_make_cc_info_mapping(
    name = "mapping_with_custom_and_builtin_duplicate",
    custom_remappings = [":custom"],
    mapping = {
        "//dwyu/cc/cc_info_mapping/test:lib_with_dep": {MAP_DIRECT_DEPS: "all"},
    },
    tags = ["manual"],
)

dwyu_make_cc_info_mapping(
    name = "mapping_with_custom_duplicate",
    custom_remappings = [
        ":custom",
        ":another_custom",
    ],
    tags = ["manual"],
)

invalid_remapping(
    name = "invalid_target_remapping",
    invalid_target = "//some:target",
)

invalid_remapping(
    name = "invalid_cc_info_remapping",
    invalid_cc_info = "not a CcInfo",
)

dwyu_make_cc_info_mapping(
    name = "mapping_with_invalid_target",
    custom_remappings = [":invalid_target_remapping"],
    tags = ["manual"],
)

dwyu_make_cc_info_mapping(
    name = "mapping_with_invalid_cc_info",
    custom_remappings = [":invalid_cc_info_remapping"],
    tags = ["manual"],
)
