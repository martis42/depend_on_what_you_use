load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_python//python:py_library.bzl", "py_library")

py_library(
    name = "lib",
    srcs = [
        "apply_fixes.py",
        "bazel_query.py",
        "buildozer_executor.py",
        "get_dwyu_reports.py",
        "search_missing_deps.py",
        "summary.py",
        "utils.py",
    ],
    visibility = [":__subpackages__"],
)

py_binary(
    name = "main",
    srcs = ["main.py"],
    # Compatibility to --noexperimental_python_import_all_repositories
    imports = ["../.."],
    visibility = ["//:__pkg__"],
    deps = [":lib"],
)
