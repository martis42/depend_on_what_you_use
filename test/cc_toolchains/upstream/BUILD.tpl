load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "use_toolchain_headers",
    hdrs = ["use_toolchain_headers.h"],
)
