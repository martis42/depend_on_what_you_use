load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "breaking_preprocessor",
    srcs = ["breaking_preprocessor.cpp"],
    deps = ["//preprocessing/support:lib_a"],
)

cc_library(
    name = "breaking_preprocessor_with_unused_dep",
    srcs = ["breaking_preprocessor.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "//preprocessing/support:lib_b",
    ],
)
