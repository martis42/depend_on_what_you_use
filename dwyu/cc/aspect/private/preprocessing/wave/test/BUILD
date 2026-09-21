load("@rules_cc//cc:cc_test.bzl", "cc_test")

cc_test(
    name = "preprocessing_hook_base_test",
    srcs = ["preprocessing_hook_base_test.cpp"],
    deps = [
        "//dwyu/cc/aspect/private/preprocessing/wave:preprocessing_hooks",
        "@boost.wave//:wave",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)
