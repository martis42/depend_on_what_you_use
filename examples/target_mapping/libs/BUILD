load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "a",
    hdrs = ["a.h"],
    visibility = ["//target_mapping:__subpackages__"],
    deps = [
        ":b",
        ":d",
    ],
)

cc_library(
    name = "b",
    hdrs = ["b.h"],
    visibility = ["//target_mapping/mapping:__pkg__"],
    deps = [":c"],
)

cc_library(
    name = "c",
    hdrs = ["c.h"],
)

cc_library(
    name = "d",
    hdrs = ["d.h"],
    deps = [":e"],
)

cc_library(
    name = "e",
    hdrs = ["e.h"],
)
