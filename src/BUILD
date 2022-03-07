load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_library(
    name = "lib",
    srcs = [
        "evaluate_includes.py",
        "get_dependencies.py",
        "parse_config.py",
        "parse_source.py",
        "std_header.py",
    ],
    visibility = [":__subpackages__"],
)

py_binary(
    name = "analyze_includes",
    srcs = ["main.py"],
    legacy_create_init = False,
    main = "main.py",
    visibility = ["//visibility:public"],
    deps = [":lib"],
)
