load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        "@boost.algorithm",
        "@boost.filesystem",
        "@boost.program_options",
    ],
)
