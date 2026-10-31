load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "foo",
    hdrs = ["foo.h"],
)

cc_library(
    name = "aggregate",
    deps = [":foo"],
)

cc_library(
    name = "bar",
    srcs = [":bar.cpp"],
)

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    deps = [
        ":aggregate",
        ":bar",
        ":foo",
    ],
)
