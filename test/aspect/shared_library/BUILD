load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library")

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
