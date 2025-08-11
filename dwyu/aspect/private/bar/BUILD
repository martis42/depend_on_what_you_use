load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "bar",
    srcs = ["bar.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        "@boost.algorithm",
        "@boost.filesystem",
        "@boost.json",
        "@boost.program_options",
    ],
)
