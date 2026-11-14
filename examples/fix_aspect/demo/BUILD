load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "my_type",
    hdrs = ["my_type.h"],
)

cc_library(
    name = "lib",
    hdrs = ["lib.h"],
    deps = [":my_type"],
)

cc_library(
    name = "use_lib",
    srcs = ["use_lib.cpp"],
    hdrs = ["use_lib.h"],
    # Missing dependency to ':my_type', which DWYU finds through ':lib'
    deps = [":lib"],
)

cc_library(
    name = "not_using_lib",
    hdrs = ["not_using_lib.h"],
    deps = [
        ":lib",  # Unused dependency
        ":my_type",
    ],
)
