load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "has_unused_dep",
    hdrs = ["has_unused_dep.h"],
    visibility = ["//visibility:public"],
    deps = [":foo"],
)

cc_library(
    name = "foo",
    hdrs = ["foo.h"],
)
