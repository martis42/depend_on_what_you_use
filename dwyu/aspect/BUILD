load("@bazel_skylib//:bzl_library.bzl", "bzl_library")

bzl_library(
    name = "factory",
    srcs = [
        "dwyu.bzl",
        "factory.bzl",
    ],
    visibility = ["//visibility:public"],
    deps = [
        "//dwyu/cc_info_mapping",
        "//dwyu/cc_toolchain_headers",
        "@rules_cc//cc:action_names_bzl",
        "@rules_cc//cc:find_cc_toolchain_bzl",
        "@rules_cc//cc/common",
    ],
)

exports_files(
    ["factory.bzl"],
    visibility = ["//docs:__pkg__"],
)
