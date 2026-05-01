load("@rules_cc//cc:cc_test.bzl", "cc_test")

cc_test(
    name = "included_file_test",
    srcs = ["included_file_test.cpp"],
    deps = [
        "//dwyu/aspect/private/preprocessing/lib:included_file",
        "@boost//:filesystem",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)
