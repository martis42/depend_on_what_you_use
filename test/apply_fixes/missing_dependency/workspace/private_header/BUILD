load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "private_header",
    srcs = [
        "bar.cpp",
        "private_bar.h",
    ],
    hdrs = ["bar.h"],
    visibility = ["//visibility:public"],
)
