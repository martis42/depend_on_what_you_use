cc_library(
    name = "lib_a",
    hdrs = ["lib_a.h"],
)

cc_library(
    name = "lib_b",
    hdrs = ["lib_b.h"],
)

cc_library(
    name = "unused_public_dep",
    srcs = ["using_lib_a.cpp"],
    deps = [
        ":lib_a",
        ":lib_b",  # unused
    ],
)

cc_library(
    name = "unused_private_dep",
    srcs = ["using_lib_a.cpp"],
    implementation_deps = [
        ":lib_a",
        ":lib_b",  # unused
    ],
)

cc_library(
    name = "public_dependency_with_private_use",
    srcs = ["using_lib_a.cpp"],
    hdrs = ["using_lib_b.h"],
    deps = [
        ":lib_a",
        ":lib_b",
    ],
)
