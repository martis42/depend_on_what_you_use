load("@rules_cc//cc:cc_test.bzl", "cc_test")

cc_test(
    name = "program_options_test",
    srcs = ["program_options_test.cpp"],
    data = ["data/multiple_options.txt"],
    deps = [
        "//dwyu/cc/private:program_options",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)

cc_test(
    name = "utils_cc_test",
    srcs = ["utils_test.cpp"],
    deps = [
        "//dwyu/cc/private:utils",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)
