load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "foo",
    hdrs = ["include/string/foo.h"],
    includes = ["include"],
)

cc_library(
    name = "bar",
    hdrs = ["include/string/foo.h"],
    strip_include_prefix = "include",
)
