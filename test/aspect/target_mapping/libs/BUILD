load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_shell//shell:sh_library.bzl", "sh_library")

cc_library(
    name = "mapped_dep",
    hdrs = ["mapped_dep.h"],
    visibility = ["//target_mapping:__subpackages__"],
    deps = [
        ":a",
        # Test traversing direct deps is robust against non C/CPP deps
        ":non_cc_thing",
        # Ensure external targets are processed just as well
        "@target_mapping_test_repo//:ext_a",
    ],
)

cc_library(
    name = "a",
    hdrs = ["a.h"],
    visibility = ["//target_mapping/mapping:__pkg__"],
    deps = [
        ":b",
        # Test traversing transitive deps is robust against non C/CPP deps
        ":non_cc_thing",
    ],
)

cc_library(
    name = "b",
    hdrs = ["b.h"],
    visibility = ["//target_mapping/mapping:__pkg__"],
)

sh_library(
    name = "non_cc_thing",
    srcs = ["non_cc_thing.sh"],
)
