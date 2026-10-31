load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "lib",
    hdrs = ["lib.h"],
)

cc_library(
    name = "lib_user",
    hdrs = ["lib_user.h"],
    deps = [":lib"],
)

cc_binary(
    name = "use_transitive_dep",
    srcs = ["use_transitive_dep.cpp"],
    deps = [":lib_user"],
)
