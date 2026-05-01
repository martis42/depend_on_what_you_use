load("@rules_cc//cc:cc_library.bzl", "cc_library")

package(default_visibility = ["//preprocessing:__subpackages__"])

cc_library(
    name = "lib_a",
    hdrs = ["lib_a.h"],
    deps = [":transitive"],
)

cc_library(
    name = "lib_b",
    hdrs = ["lib_b.h"],
    deps = [":transitive"],
)

cc_library(
    name = "lib_c",
    hdrs = ["lib_c.h"],
    deps = [":transitive"],
)

cc_library(
    name = "lib_d",
    hdrs = ["lib_d.h"],
    deps = [":transitive"],
)

cc_library(
    name = "lib_e",
    hdrs = ["lib_e.h"],
    deps = [":transitive"],
)

cc_library(
    name = "transitive",
    hdrs = ["transitive.h"],
)
