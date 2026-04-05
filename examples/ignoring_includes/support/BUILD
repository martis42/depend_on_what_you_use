load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "foo",
    visibility = ["//visibility:public"],
    deps = [
        ":some_header",
        "//ignoring_includes/support/foo:bar",
    ],
)

cc_library(
    name = "some_header",
    hdrs = ["some_header.h"],
    visibility = ["//ignoring_includes/support:__subpackages__"],
)
