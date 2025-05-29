load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "lib_a",
    hdrs = ["lib_a.h"],
)

cc_library(
    name = "lib_b",
    hdrs = ["lib_b.h"],
)

cc_library(
    name = "lib_c",
    hdrs = ["lib_c.h"],
    deps = [
        ":lib_a",
        ":lib_b",
    ],
)

cc_library(
    name = "unused_public_dep",
    srcs = ["using_a.cpp"],
    deps = [
        ":lib_a",
        ":lib_b",  # unused
        ":lib_c",  # unused
    ],
)

cc_library(
    name = "unused_private_dep",
    srcs = ["using_a.cpp"],
    implementation_deps = [
        ":lib_a",
        ":lib_b",  # unused
        ":lib_c",  # unused
    ],
)
