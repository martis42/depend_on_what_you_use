load("@bazel_skylib//:bzl_library.bzl", "bzl_library")

bzl_library(
    name = "cc_toolchain_headers",
    srcs = [
        "cc_toolchain_headers.bzl",
        "providers.bzl",
    ],
    visibility = ["//visibility:public"],
    deps = [
        "//src/cc_toolchain_headers/private:gather_cc_toolchain_headers_bzl",
        "//src/utils",
    ],
)
