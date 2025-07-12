load("@rules_python//python:defs.bzl", "py_test")
load(":extract_include_paths_test.bzl", "extract_include_paths_test_suite")

py_test(
    name = "gather_toolchain_headers_test",
    srcs = ["gather_toolchain_headers_test.py"],
    data = glob(["data/**/*"]),
    deps = ["//src/toolchain_headers/private:gather_toolchain_headers"],
)

extract_include_paths_test_suite(name = "extract_include_paths_test")
