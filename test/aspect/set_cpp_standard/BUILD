load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "cpp_lib",
    srcs = ["cpp_lib.cpp"],
    hdrs = ["cpp_lib.h"],
)

cc_library(
    name = "use_specific_cpp_standard",
    hdrs = ["use_specific_cpp_standard.h"],
    copts = ["-std=c++17"],
)
