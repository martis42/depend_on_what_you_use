load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "use_has_include",
    hdrs = ["use_has_include.h"],
    deps = [
        ":lib_a",
        ":lib_b",
    ],
)

cc_library(
    name = "lib_a",
    hdrs = ["lib_a.h"],
    deps = [":transitive_dep"],
)

cc_library(
    name = "lib_b",
    hdrs = ["lib_b.h"],
    deps = [":transitive_dep"],
)

cc_library(
    name = "transitive_dep",
    hdrs = ["transitive_dep.h"],
)
