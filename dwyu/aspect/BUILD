load("@bazel_skylib//:bzl_library.bzl", "bzl_library")

bzl_library(
    name = "dwyu_bzl",
    srcs = ["dwyu.bzl"],
    visibility = ["//visibility:public"],
    deps = [
        "//dwyu/cc_info_mapping:providers_bzl",
        "//dwyu/private:utils_bzl",
        "@rules_cc//cc:action_names_bzl",
        "@rules_cc//cc:find_cc_toolchain_bzl",
        "@rules_cc//cc/common",
    ],
)

bzl_library(
    name = "factory_bzl",
    srcs = ["factory.bzl"],
    visibility = ["//visibility:public"],
    deps = [
        ":dwyu_bzl",
        "//dwyu/cc_info_mapping:providers_bzl",
        "@rules_cc//cc:find_cc_toolchain_bzl",
        "@rules_cc//cc/common",
    ],
)

exports_files(
    ["factory.bzl"],
    visibility = ["//docs:__pkg__"],
)
