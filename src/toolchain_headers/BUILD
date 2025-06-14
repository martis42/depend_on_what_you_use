load("@rules_python//python:defs.bzl", "py_binary")
load(":gather_toolchain_headers.bzl", "gather_toolchain_headers")

py_binary(
    name = "gather_toolchain_headers",
    srcs = ["gather_toolchain_headers.py"],
    visibility = [":__subpackages__"],
)

gather_toolchain_headers(
    name = "toolchain_headers",
    visibility = ["//visibility:public"],
)
