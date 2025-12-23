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
    name = "included_file_test",
    srcs = ["included_file_test.cpp"],
    deps = [
        "//dwyu/aspect/private/preprocessing:included_file",
        "@boost//:filesystem",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)
