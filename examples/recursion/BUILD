load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "use_lib",
    hdrs = ["use_lib.h"],
    deps = [":faulty_lib"],
)

cc_library(
    name = "faulty_lib",
    hdrs = ["lib.h"],
    deps = [":unused_dep"],
)

cc_library(
    name = "unused_dep",
    hdrs = ["unused_dep.h"],
)
