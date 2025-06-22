load("@bazel_skylib//:bzl_library.bzl", "bzl_library")

bzl_library(
    name = "toolchain_headers",
    srcs = [
        "providers.bzl",
        "toolchain_headers.bzl",
    ],
    visibility = ["//visibility:public"],
    deps = ["//src/toolchain_headers/private:gather_toolchain_headers_bzl"],
)

exports_files(
    ["toolchain_headers.bzl"],
    visibility = ["//docs:__pkg__"],
)
