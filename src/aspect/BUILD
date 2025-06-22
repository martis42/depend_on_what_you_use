load("@bazel_skylib//:bzl_library.bzl", "bzl_library")
load("@rules_python//python:py_binary.bzl", "py_binary")

py_binary(
    name = "process_target",
    srcs = ["process_target.py"],
    visibility = ["//visibility:public"],
)

bzl_library(
    name = "factory",
    srcs = [
        "dwyu.bzl",
        "factory.bzl",
    ],
    visibility = ["//visibility:public"],
    deps = [
        "//src/cc_info_mapping",
        "//src/cc_toolchain_headers",
        "@rules_cc//cc:action_names_bzl",
        "@rules_cc//cc:find_cc_toolchain_bzl",
        "@rules_cc//cc/common",
    ],
)

exports_files(
    ["factory.bzl"],
    visibility = ["//docs:__pkg__"],
)
