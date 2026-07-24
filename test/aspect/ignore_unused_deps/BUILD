load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "foo",
    hdrs = ["foo.h"],
)

cc_library(
    name = "lib_with_unused_deps",
    srcs = ["lib.cpp"],
    hdrs = ["lib.h"],
    implementation_deps = ["@ignore_unused_deps_test_repo//:ext"],
    deps = [":foo"],
)
