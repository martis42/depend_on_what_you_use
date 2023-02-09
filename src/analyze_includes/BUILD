load("@rules_python//python:defs.bzl", "py_binary", "py_library")
load("//:requirements.bzl", "requirement")

py_library(
    name = "lib",
    srcs = [
        "evaluate_includes.py",
        "parse_config.py",
        "parse_source.py",
        "std_header.py",
        "system_under_inspection.py",
    ],
    visibility = [":__subpackages__"],
    deps = [
        requirement("libclang"),
    ],
)

py_binary(
    name = "analyze_includes",
    srcs = ["main.py"],
    legacy_create_init = False,
    main = "main.py",
    visibility = ["//visibility:public"],
    deps = [":lib"],
)
