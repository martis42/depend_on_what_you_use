load("@rules_python//python:py_test.bzl", "py_test")

py_test(
    name = "expected_result_test",
    srcs = [
        "expected_result.py",
        "expected_result_test.py",
    ],
    deps = ["@depend_on_what_you_use//test/support"],
)

py_test(
    name = "test_case_test",
    srcs = [
        "expected_result.py",
        "test_case.py",
        "test_case_test.py",
        "version.py",
    ],
    deps = ["@depend_on_what_you_use//test/support"],
)

py_test(
    name = "version_test",
    srcs = [
        "version.py",
        "version_test.py",
    ],
)
