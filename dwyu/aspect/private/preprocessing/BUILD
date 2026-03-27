load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "extract_includes",
    srcs = ["extract_includes.cpp"],
    hdrs = ["extract_includes.h"],
    visibility = [":__subpackages__"],
)

cc_library(
    name = "included_file",
    srcs = ["included_file.cpp"],
    hdrs = ["included_file.h"],
    visibility = ["//dwyu/aspect/private:__subpackages__"],
    deps = ["@boost//:filesystem"],
)

cc_library(
    name = "preprocessing_hooks",
    hdrs = ["preprocessing_hooks.h"],
    visibility = [":__subpackages__"],
    deps = [
        ":included_file",
        "@boost.wave//:wave",
        "@boost//:filesystem",
    ],
)

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        ":included_file",
        ":preprocessing_hooks",
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
        "@boost.wave//:wave",
        "@nlohmann_json//:singleheader-json",
    ],
)

cc_binary(
    name = "main_no_preprocessing",
    srcs = ["main_no_preprocessing.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        ":extract_includes",
        ":included_file",
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
        "@boost.wave//:wave",
        "@boost//:filesystem",
        "@nlohmann_json//:singleheader-json",
    ],
)
