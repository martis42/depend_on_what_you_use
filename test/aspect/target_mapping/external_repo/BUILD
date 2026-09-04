load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "ext_a",
    hdrs = ["ext_a.h"],
    visibility = ["//visibility:public"],
    deps = [":ext_b"],
)

cc_library(
    name = "ext_b",
    hdrs = ["ext_b.h"],
)
