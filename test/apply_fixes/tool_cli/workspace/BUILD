cc_library(
    name = "lib",
    hdrs = ["lib.h"],
    visibility = [":__subpackages__"],
)

cc_binary(
    name = "binary",
    srcs = ["binary.cpp"],
    deps = [
        ":lib",  # unused
    ],
)

cc_binary(
    name = "another_binary",
    srcs = ["binary.cpp"],
    deps = [
        ":lib",  # unused
    ],
)
