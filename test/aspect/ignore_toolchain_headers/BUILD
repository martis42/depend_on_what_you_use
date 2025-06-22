load("@rules_cc//cc:cc_library.bzl", "cc_library")
load(":custom_ignored_headers.bzl", "custom_cc_toolchain_headers_info")

custom_cc_toolchain_headers_info(
    name = "custom_cc_toolchain_headers_info",
)

cc_library(
    name = "use_toolchain_header",
    hdrs = ["use_toolchain_header.h"],
)

cc_library(
    name = "use_custom_toolchain_header",
    hdrs = ["use_custom_toolchain_header.h"],
)
