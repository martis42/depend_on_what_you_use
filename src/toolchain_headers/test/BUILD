load("@rules_python//python:defs.bzl", "py_test")
load(":gather_toolchain_headers_test.bzl", "gather_toolchain_headers_test_suite")

py_test(
    name = "gather_toolchain_headers_test",
    srcs = ["gather_toolchain_headers_test.py"],
    data = glob(["data/**/*"]),
    deps = ["//src/toolchain_headers:gather_toolchain_headers"],
)

gather_toolchain_headers_test_suite(name = "dwyu_aspect_tests")
