load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "included_file",
    srcs = ["included_file.cpp"],
    hdrs = ["included_file.h"],
    visibility = ["//dwyu/aspect/private:__subpackages__"],
    deps = ["@boost//:filesystem"],
)
