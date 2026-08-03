load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "broken_a",
    hdrs = ["a.h"],
    deps = ["//skip_targets:unused_lib"],
)

cc_library(
    name = "broken_b",
    hdrs = ["b.h"],
    deps = ["//skip_targets:unused_lib"],
)
