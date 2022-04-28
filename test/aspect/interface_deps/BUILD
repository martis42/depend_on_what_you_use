cc_library(
    name = "a",
    hdrs = ["a.h"],
)

cc_library(
    name = "b",
    hdrs = ["b.h"],
)

cc_library(
    name = "valid_deps",
    srcs = ["use_a_and_b.cpp"],
    hdrs = ["use_a_and_b.h"],
    interface_deps = [":a"],
    deps = [":b"],
)

cc_library(
    name = "invalid_deps",
    srcs = ["use_a_and_b.cpp"],
    hdrs = ["use_a_and_b.h"],
    interface_deps = [
        ":a",
        ":b",
    ],
)
