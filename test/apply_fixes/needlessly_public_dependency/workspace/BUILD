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
    name = "public_dependency_with_private_use",
    srcs = ["using_a_and_b.cpp"],
    hdrs = ["using_c.h"],
    deps = [
        ":lib_a",  # only used privately
        ":lib_b",  # only used privately
        ":lib_c",
    ],
)
