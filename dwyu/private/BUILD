load("@bazel_skylib//:bzl_library.bzl", "bzl_library")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

bzl_library(
    name = "utils_bzl",
    srcs = [
        "utils.bzl",
    ],
    visibility = ["//dwyu:__subpackages__"],
)

cc_library(
    name = "program_options",
    srcs = ["program_options.cpp"],
    hdrs = ["program_options.h"],
    visibility = ["//dwyu:__subpackages__"],
    deps = [":utils"],
)

cc_library(
    name = "utils",
    srcs = ["utils.cpp"],
    hdrs = ["utils.h"],
    visibility = ["//dwyu:__subpackages__"],
)
