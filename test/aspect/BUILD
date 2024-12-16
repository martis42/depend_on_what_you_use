load("@rules_python//python:py_library.bzl", "py_library")
load("@rules_python//python:py_test.bzl", "py_test")

py_library(
    name = "expected_result",
    testonly = True,
    srcs = ["expected_result.py"],
    deps = ["@depend_on_what_you_use//test/support"],
)

py_test(
    name = "expected_result_test",
    srcs = ["expected_result_test.py"],
    deps = [":expected_result"],
)

py_test(
    name = "test_case_test",
    srcs = [
        "test_case.py",
        "test_case_test.py",
    ],
    deps = [":expected_result"],
)

py_test(
    name = "version_test",
    srcs = [
        "version.py",
        "version_test.py",
    ],
)
