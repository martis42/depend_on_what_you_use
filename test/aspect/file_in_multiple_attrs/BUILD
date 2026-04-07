load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "lib",
    srcs = [
        "lib.cc",  # NOTE: This has to be here even though the duplicate file is the lib.h
        "lib.h",
    ],
    hdrs = ["lib.h"],
)
