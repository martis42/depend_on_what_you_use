load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "lib",
    hdrs = ["lib.h"],
    visibility = ["//skip_features:__subpackages__"],
)

cc_library(
    name = "lib_indirection",
    hdrs = ["foo.h"],
    visibility = ["//skip_features:__subpackages__"],
    deps = [":lib"],
)
