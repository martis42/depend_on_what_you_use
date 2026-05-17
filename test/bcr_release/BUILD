load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "ok",
    hdrs = ["ok.h"],
)

cc_library(
    name = "failure",
    hdrs = ["failure.h"],
    deps = [":ok"],
)
