load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "foo_lib",
    srcs = ["foo.cc"],
    hdrs = ["foo.h"],
)

cc_binary(
    name = "libfoo.so",
    linkshared = True,
    deps = [
        ":foo_lib",
    ],
)
