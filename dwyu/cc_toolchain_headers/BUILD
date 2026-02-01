load("@bazel_skylib//:bzl_library.bzl", "bzl_library")

bzl_library(
    name = "cc_toolchain_headers_bzl",
    srcs = ["cc_toolchain_headers.bzl"],
    visibility = ["//visibility:public"],
    deps = [
        ":providers_bzl",
        "//dwyu/cc_toolchain_headers/private:gather_cc_toolchain_headers_bzl",
    ],
)

bzl_library(
    name = "providers_bzl",
    srcs = ["providers.bzl"],
    visibility = ["//visibility:public"],
)
