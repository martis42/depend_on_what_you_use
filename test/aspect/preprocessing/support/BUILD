load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "lib_a",
    hdrs = ["lib_a.h"],
    visibility = ["//preprocessing:__pkg__"],
    deps = [":transitive"],
)

cc_library(
    name = "lib_b",
    hdrs = ["lib_b.h"],
    visibility = ["//preprocessing:__pkg__"],
    deps = [":transitive"],
)

cc_library(
    name = "lib_c",
    hdrs = ["lib_c.h"],
    visibility = ["//preprocessing:__pkg__"],
    deps = [":transitive"],
)

cc_library(
    name = "lib_d",
    hdrs = ["lib_d.h"],
    visibility = ["//preprocessing:__pkg__"],
    deps = [":transitive"],
)

cc_library(
    name = "lib_e",
    hdrs = ["lib_e.h"],
    visibility = ["//preprocessing:__pkg__"],
    deps = [":transitive"],
)

cc_library(
    name = "transitive",
    hdrs = ["transitive.h"],
)
