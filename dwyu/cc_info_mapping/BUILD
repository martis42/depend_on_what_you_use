load("@bazel_skylib//:bzl_library.bzl", "bzl_library")

bzl_library(
    name = "cc_info_mapping_bzl",
    srcs = ["cc_info_mapping.bzl"],
    visibility = ["//visibility:public"],
    deps = [
        ":providers_bzl",
        "//dwyu/cc_info_mapping/private:cc_info_mapping_impl_bzl",
        "//dwyu/private:utils_bzl",
    ],
)

bzl_library(
    name = "providers_bzl",
    srcs = ["providers.bzl"],
    visibility = ["//visibility:public"],
)

exports_files(
    ["cc_info_mapping.bzl"],
    visibility = ["//docs:__pkg__"],
)
