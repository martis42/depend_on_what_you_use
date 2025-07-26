load("@rules_python//python:defs.bzl", "py_test")
load(":gather_cc_toolchain_headers_test.bzl", "gather_cc_toolchain_headers_test_suite")

py_test(
    name = "gather_cc_toolchain_headers_tool_test",
    srcs = ["gather_cc_toolchain_headers_test.py"],
    data = glob(["data/**/*"]),
    main = "gather_cc_toolchain_headers_test.py",
    deps = ["//dwyu/cc_toolchain_headers/private:gather_cc_toolchain_headers_tool"],
)

gather_cc_toolchain_headers_test_suite(name = "gather_cc_toolchain_headers_rule_test")
