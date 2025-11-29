load("@rules_cc//cc:cc_test.bzl", "cc_test")

cc_test(
    name = "extract_includes_test",
    srcs = ["extract_includes_test.cpp"],
    data = ["data/commented_includes.h"],
    deps = [
        "//dwyu/aspect/private/preprocessing:extract_includes",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)

cc_test(
    name = "preprocessing_hooks_test",
    srcs = ["preprocessing_hooks_test.cpp"],
    deps = [
        "//dwyu/aspect/private/preprocessing:preprocessing_hooks",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)
