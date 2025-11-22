load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "ext_lib",
    hdrs = ["ext_lib.h"],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "lib_with_includes",
    hdrs = ["ext/dir/ext_lib_with_includes.h"],
    includes = ["ext"],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "lib_with_strip_prefix",
    hdrs = ["ext/dir/ext_lib_with_strip_prefix.h"],
    strip_include_prefix = "ext/dir",
    visibility = ["//visibility:public"],
)

cc_library(
    name = "lib_with_add_prefix",
    hdrs = ["ext/dir/ext_lib_with_add_prefix.h"],
    include_prefix = "some/prefix",
    visibility = ["//visibility:public"],
)
