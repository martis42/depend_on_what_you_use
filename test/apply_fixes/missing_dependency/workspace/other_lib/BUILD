load("@rules_cc//cc:cc_library.bzl", "cc_library")

# We use this library to prove that multiple header with the same name existing in the dependency is not a problem if
# they are included with their full path
cc_library(
    name = "other_lib",
    hdrs = ["foo.h"],
    visibility = ["//visibility:public"],
)
