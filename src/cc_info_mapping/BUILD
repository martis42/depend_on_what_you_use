load("@bazel_skylib//:bzl_library.bzl", "bzl_library")

bzl_library(
    name = "cc_info_mapping",
    srcs = [
        "cc_info_mapping.bzl",
        "providers.bzl",
        "@bazel_tools//tools/cpp:toolchain_utils.bzl",
        "@rules_cc//cc:bzl_srcs",
    ],
    visibility = ["//visibility:public"],
    deps = [
        "//src/cc_info_mapping/private:bzl_srcs",
        "//src/utils",
    ],
)

exports_files(
    ["cc_info_mapping.bzl"],
    visibility = ["//docs:__pkg__"],
)
