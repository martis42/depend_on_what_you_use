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
)

cc_library(
    name = "unused_public_dep",
    srcs = ["using_lib_a.cpp"],
    deps = [
        ":lib_a",
        ":lib_b",  # unused
        ":lib_c",  # unused
    ],
)

cc_library(
    name = "unused_private_dep",
    srcs = ["using_lib_a.cpp"],
    implementation_deps = [
        ":lib_a",
        ":lib_b",  # unused
        ":lib_c",  # unused
    ],
)

cc_library(
    name = "public_dependency_with_private_use",
    srcs = [
        "using_lib_a.cpp",
        "using_lib_b.cpp",
    ],
    hdrs = ["using_lib_c.h"],
    deps = [
        ":lib_a",  # only used privately
        ":lib_b",  # only used privately
        ":lib_c",
    ],
)
