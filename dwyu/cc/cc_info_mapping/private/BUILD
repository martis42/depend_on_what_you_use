load("@bazel_skylib//:bzl_library.bzl", "bzl_library")

bzl_library(
    name = "cc_info_mapping_impl_bzl",
    srcs = [
        "common.bzl",
        "direct_deps.bzl",
        "direct_deps_greedily.bzl",
        "explicit.bzl",
        "explicit_deps.bzl",
        "transitive_deps.bzl",
        "transitive_deps_greedily.bzl",
    ],
    visibility = ["//dwyu/cc/cc_info_mapping:__pkg__"],
    deps = [
        "//dwyu/cc/cc_info_mapping:providers_bzl",
        "@rules_cc//cc/common",
    ],
)
