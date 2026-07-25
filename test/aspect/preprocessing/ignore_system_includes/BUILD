load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_binary(
    name = "use_system_lib",
    srcs = ["use_system_lib.cpp"],
    deps = [
        ":system_switch",
        "//preprocessing/support:lib_a",
    ],
)

cc_binary(
    name = "use_system_lib_with_preprocessing_chosen_by_tag",
    srcs = ["use_system_lib.cpp"],
    tags = ["dwyu:preprocessing_mode=ignore_system_includes"],
    deps = [
        ":system_switch",
        "//preprocessing/support:lib_a",
    ],
)

cc_library(
    name = "system_switch",
    hdrs = ["system_switch.h"],
    includes = ["."],
)
