load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "program_options",
    srcs = ["program_options.cpp"],
    hdrs = ["program_options.h"],
    implementation_deps = [":utils"],
    visibility = ["//dwyu:__subpackages__"],
)

cc_library(
    name = "utils",
    srcs = ["utils.cpp"],
    hdrs = ["utils.h"],
    visibility = ["//dwyu:__subpackages__"],
)
