load("@bazel_skylib//:bzl_library.bzl", "bzl_library")

bzl_library(
    name = "utils",
    srcs = [
        "utils.bzl",
    ],
    visibility = ["//visibility:public"],
)

bzl_library(
    name = "rules_cc_bzl_srcs",
    srcs = [
        "@bazel_tools//tools/cpp:toolchain_utils.bzl",
        "@rules_cc//cc:bzl_srcs",
    ],
    visibility = ["//src:__subpackages__"],
)
