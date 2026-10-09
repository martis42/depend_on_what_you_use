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

cc_library(
    name = "lib_f",
    hdrs = ["lib_f.h"],
    deps = [":transitive"],
)

cc_library(
    name = "lib_g",
    hdrs = ["lib_g.h"],
    deps = [":transitive"],
)

cc_library(
    name = "lib_h",
    hdrs = ["lib_h.h"],
    deps = [":transitive"],
)

cc_library(
    name = "angle_lib_a",
    hdrs = ["angle_lib_a.h"],
    includes = ["."],
)

cc_library(
    name = "angle_lib_b",
    hdrs = ["angle_lib_b.h"],
    includes = ["."],
)

cc_library(
    name = "angle_lib_c",
    hdrs = ["angle_lib_c.h"],
    includes = ["."],
)
