load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_library(
    name = "lib",
    srcs = [
        "apply_fixes.py",
        "buildozer_executor.py",
        "summary.py",
    ],
    visibility = [":__subpackages__"],
)

py_binary(
    name = "main",
    srcs = ["main.py"],
    visibility = ["//:__pkg__"],
    deps = [":lib"],
)
