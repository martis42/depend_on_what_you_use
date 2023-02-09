load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library")

cc_library(
    name = "naughty",
    hdrs = ["naughty.h"],
)

cc_library(
    name = "a",
    hdrs = ["a.h"],
)

cc_library(
    name = "b",
    srcs = ["b.cpp"],
    hdrs = ["b.h"],
)

cc_binary(
    name = "a_or_b",
    srcs = ["main.cpp"],
    deps = [
        ":a",
        ":naughty",
    ],
)
