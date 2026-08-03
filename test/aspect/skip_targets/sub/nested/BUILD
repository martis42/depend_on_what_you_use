load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "broken_nested",
    hdrs = ["nested.h"],
    deps = ["//skip_targets:unused_lib"],
)
