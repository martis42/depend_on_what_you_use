load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "foo",
    hdrs = ["foo.h"],
)

cc_library(
    name = "bar",
    hdrs = ["bar.h"],
    deps = [":foo"],
)

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    deps = [":bar"],
)

cc_library(
    name = "transitive_usage_through_impl_deps",
    srcs = ["transitive_usage_through_impl_deps.h"],
    deps = [":bar"],
)
