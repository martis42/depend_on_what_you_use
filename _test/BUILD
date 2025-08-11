load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "foo",
    srcs = ["foo.cpp"],
    deps = [
        ":a",
        "//_test/sub:lib",
    ],
)

cc_library(
    name = "a",
    hdrs = ["a.h"],
    deps = [":b"],
)

cc_library(
    name = "b",
    hdrs = ["b.h"],
)
