load("@rules_python//python:py_library.bzl", "py_library")

py_library(
    name = "pcpp",
    srcs = glob(["pcpp/**/*"]),
    imports = ["."],
    # Users are not supposed to reuse this directly. However, since users can include this project under
    # a custom name, we can't restrict visibility.
    visibility = ["//visibility:public"],
)
