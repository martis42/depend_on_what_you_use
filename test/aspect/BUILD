load("@rules_python//python:defs.bzl", "py_library", "py_test")

py_test(
    name = "result_test",
    srcs = [
        "result.py",
        "result_test.py",
    ],
)

py_test(
    name = "test_case_test",
    srcs = [
        "test_case.py",
        "test_case_test.py",
    ],
)

py_test(
    name = "version_test",
    srcs = [
        "version.py",
        "version_test.py",
    ],
)

# Helper target to enable mypy
py_library(
    name = "python_files",
    srcs = glob(["**/*.py"]),
)
