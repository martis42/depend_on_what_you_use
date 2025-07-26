load("@bazel_skylib//:bzl_library.bzl", "bzl_library")

bzl_library(
    name = "cc_info_mapping",
    srcs = [
        "cc_info_mapping.bzl",
        "providers.bzl",
    ],
    visibility = ["//visibility:public"],
    deps = [
        "//dwyu/cc_info_mapping/private:cc_info_mapping_impl_bzl",
        "//dwyu/private:utils_bzl",
    ],
)

exports_files(
    ["cc_info_mapping.bzl"],
    visibility = ["//docs:__pkg__"],
)
