load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_python//python:py_library.bzl", "py_library")

py_library(
    name = "lib",
    srcs = [
        "evaluate_includes.py",
        "parse_config.py",
        "parse_source.py",
        "result.py",
        "std_header.py",
        "system_under_inspection.py",
    ],
    visibility = [":__subpackages__"],
    deps = ["@dwyu_pcpp//:pcpp"],
)

py_binary(
    name = "analyze_includes",
    srcs = ["main.py"],
    # Compatibility to --noexperimental_python_import_all_repositories
    imports = ["../../../.."],
    legacy_create_init = False,
    main = "main.py",
    visibility = ["//visibility:public"],
    deps = [":lib"],
)
