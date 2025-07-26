load("@rules_python//python:py_binary.bzl", "py_binary")
load("//src/cc_toolchain_headers:cc_toolchain_headers.bzl", "dwyu_gather_cc_toolchain_headers")
load(":cc_toolchain_headers_stub.bzl", "cc_toolchain_headers_stub")

dwyu_gather_cc_toolchain_headers(
    name = "cc_toolchain_headers",
    visibility = ["//visibility:public"],
)

cc_toolchain_headers_stub(
    name = "cc_toolchain_headers_stub",
    visibility = ["//visibility:public"],
)

py_binary(
    name = "process_target",
    srcs = ["process_target.py"],
    visibility = ["//visibility:public"],
)
