load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_library(
    name = "lib",
    srcs = ["lib.py"],
)

py_binary(
    name = "main",
    srcs = ["main.py"],
    # Compatibility to --noexperimental_python_import_all_repositories
    imports = ["../../../.."],
    legacy_create_init = False,
    visibility = ["//visibility:public"],
    deps = [
        ":lib",
        "//dwyu/aspect/private/analyze_includes:lib",
    ],
)
