load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "lib_a",
    hdrs = ["a.h"],
)

cc_library(
    name = "lib_b",
    hdrs = ["b.h"],
    deps = [":lib_a"],
)

alias(
    name = "alias_a",
    actual = ":lib_a",
)

alias(
    name = "alias_b",
    actual = ":lib_b",
)

cc_binary(
    name = "use_a_transitively",
    srcs = ["use_a_and_b.cpp"],
    deps = [":alias_b"],
)

cc_binary(
    name = "use_a_directly",
    srcs = ["use_a_and_b.cpp"],
    deps = [
        ":alias_a",
        ":alias_b",
    ],
)

cc_binary(
    name = "unused_dependency",
    srcs = ["no_dependencies.cpp"],
    deps = [":alias_a"],
)
