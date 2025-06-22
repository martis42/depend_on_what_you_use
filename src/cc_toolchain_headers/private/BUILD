load("@bazel_skylib//:bzl_library.bzl", "bzl_library")
load("@rules_python//python:defs.bzl", "py_binary")

py_binary(
    name = "gather_cc_toolchain_headers_tool",
    srcs = ["gather_cc_toolchain_headers.py"],
    main = "gather_cc_toolchain_headers.py",
    visibility = ["//visibility:public"],
)

bzl_library(
    name = "gather_cc_toolchain_headers_bzl",
    srcs = ["gather_cc_toolchain_headers.bzl"],
    visibility = ["//src/cc_toolchain_headers:__pkg__"],
    deps = [
        "@rules_cc//cc:action_names_bzl",
        "@rules_cc//cc:find_cc_toolchain_bzl",
        "@rules_cc//cc/common",
    ],
)

exports_files(["empty.cpp"])
