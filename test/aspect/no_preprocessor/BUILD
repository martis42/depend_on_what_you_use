# Analysis of this can only succeed when ignoring preprocessing, as otherwise one dependency would be unused
cc_library(
    name = "use_libs",
    hdrs = ["use_libs.h"],
    deps = [
        ":lib_a",
        ":lib_b",
    ],
)

cc_library(
    name = "lib_a",
    hdrs = ["lib_a.h"],
)

cc_library(
    name = "lib_b",
    hdrs = ["lib_b.h"],
)
