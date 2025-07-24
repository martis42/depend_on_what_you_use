load("@bazel_skylib//:bzl_library.bzl", "bzl_library")

bzl_library(
    name = "cc_info_mapping_impl_bzl",
    srcs = [
        "direct_deps.bzl",
        "explicit.bzl",
        "providers.bzl",
        "transitive_deps.bzl",
    ],
    visibility = ["//src/cc_info_mapping:__pkg__"],
    deps = ["@rules_cc//cc/common"],
)
