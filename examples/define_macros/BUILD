load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    deps = ["lib"],
)

cc_library(
    name = "lib",
    hdrs = ["lib.h"],
    deps = [
        ":transitive_dep_a",
        ":transitive_dep_b",
    ],
)

cc_library(
    name = "transitive_dep_a",
    hdrs = ["transitive_dep_a.h"],
)

cc_library(
    name = "transitive_dep_b",
    hdrs = ["transitive_dep_b.h"],
)
