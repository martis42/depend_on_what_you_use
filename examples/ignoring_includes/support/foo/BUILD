load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "bar",
    hdrs = [
        "bar_1.h",
        "bar_2.h",
    ],
    visibility = ["//ignoring_includes/support:__subpackages__"],
)
