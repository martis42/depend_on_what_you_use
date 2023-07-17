load("@rules_python//python:defs.bzl", "py_binary")

exports_files(["private/dwyu_empty_config.json"])

py_binary(
    name = "process_target",
    srcs = ["process_target.py"],
    visibility = ["//visibility:public"],
)
