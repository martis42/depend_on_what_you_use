load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_library(
    name = "lib",
    srcs = [
        "apply_fixes.py",
        "bazel_query.py",
        "buildozer_executor.py",
        "search_missing_deps.py",
        "summary.py",
        "utils.py",
    ],
    visibility = [":__subpackages__"],
)

py_binary(
    name = "main",
    srcs = ["main.py"],
    visibility = ["//:__pkg__"],
    deps = [":lib"],
)
