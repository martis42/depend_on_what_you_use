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

cc_library(
    name = "system_switch",
    hdrs = ["system_switch.h"],
    includes = ["."],
)
