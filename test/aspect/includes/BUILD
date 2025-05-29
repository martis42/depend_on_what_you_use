load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "includes",
    srcs = ["includes.cpp"],
    hdrs = ["some/sub/dir/includes.h"],
    includes = [
        "some",
        "some/sub",
    ],
)

cc_binary(
    name = "use_includes",
    srcs = ["use_includes.cpp"],
    deps = [":includes"],
)
