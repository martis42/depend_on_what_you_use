load(":toolchain_headers_info_test.bzl", "toolchain_headers_info_tests")

toolchain_headers_info_tests(
    expected_headers = [
        "buzz.h",
        "buzz/buzz.h",
        "fizz",
        "foobar.h",
    ],
    headers_info = "@depend_on_what_you_use//src/aspect/support:cc_toolchain_headers",
)
