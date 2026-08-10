load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_shell//shell:sh_library.bzl", "sh_library")

cc_library(
    name = "a",
    hdrs = ["a.h"],
    visibility = ["//target_mapping:__subpackages__"],
    deps = [
        ":b",
        # Test traversing direct deps is robust against non C/CPP deps
        ":non_cc_thing",
    ],
)

cc_library(
    name = "b",
    hdrs = ["b.h"],
    visibility = ["//target_mapping/mapping:__pkg__"],
    deps = [
        ":c",
        # Test traversing transitive deps is robust against non C/CPP deps
        ":non_cc_thing",
    ],
)

cc_library(
    name = "c",
    hdrs = ["c.h"],
)

# Used to test the 'filter' feature of dwyu_make_cc_info_mapping, combining an internal and an external dependency.
cc_library(
    name = "with_external_dep",
    hdrs = ["with_external_dep.h"],
    visibility = ["//target_mapping:__subpackages__"],
    deps = [
        ":b",
        "@target_mapping_test_repo//:ext",
    ],
)

sh_library(
    name = "non_cc_thing",
    srcs = ["non_cc_thing.sh"],
)
