load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "use_external_libs",
    hdrs = ["use_external_libs.h"],
    deps = [
        "@external_test_repo//:ext_bar",
        "@external_test_repo//:ext_foo",
    ],
)
