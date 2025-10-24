load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "preprocessing_hooks",
    hdrs = ["preprocessing_hooks.h"],
    visibility = [":__subpackages__"],
    deps = ["@boost.wave//:wave"],
)

cc_binary(
    name = "main",
    srcs = [
        "main.cpp",
        "preprocessing_hooks.h",
    ],
    visibility = ["//visibility:public"],
    deps = [
        ":preprocessing_hooks",
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
        "@boost.wave//:wave",
        "@nlohmann_json//:json",
    ],
)
