load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "foo",
    hdrs = ["foo.h"],
)

cc_library(
    name = "use_foo",
    hdrs = ["use_foo.h"],
    deps = [":foo"],
)

cc_library(
    name = "indirection",
    deps = [":foo"],
)

cc_library(
    name = "use_foo_transitively",
    hdrs = ["use_foo.h"],
    deps = [":indirection"],
)
