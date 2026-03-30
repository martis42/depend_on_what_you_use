load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "includes",
    hdrs = ["includes.h"],
    includes = ["."],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "include_prefix",
    hdrs = [
        "virtual_1.h",
        "virtual_2.h",
    ],
    include_prefix = "foo/bar",
    visibility = ["//visibility:public"],
)

cc_library(
    name = "strip_include_prefix",
    hdrs = [
        "sub/sub_1.h",
        "sub/sub_2.h",
    ],
    strip_include_prefix = "sub",
    visibility = ["//visibility:public"],
)

cc_library(
    name = "prefixed_and_stripped",
    hdrs = ["sub/sub_3.h"],
    include_prefix = "foo/bar",
    strip_include_prefix = "sub",
    visibility = ["//visibility:public"],
)
