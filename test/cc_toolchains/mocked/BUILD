load(":toolchain_headers_info_test.bzl", "toolchain_headers_info_test")

toolchain_headers_info_test(
    name = "classic_toolchain_header_discovery_test",
    expected_headers = [
        "buzz.h",
        "buzz/buzz.h",
        "fizz",
        "foo/foo.h",
        "foobar.h",
        "tik",
        "tik/tik",
        "tik/tok/tok.h",
        "tok/tok.h",
    ],
    headers_info = "@depend_on_what_you_use//src/aspect/support:toolchain_headers",
    toolchain = "@test_toolchain_classic//:toolchain",
)

toolchain_headers_info_test(
    name = "rule_based_toolchain_header_discovery_test",
    expected_headers = [
        "buzz.h",
        "buzz/buzz.h",
        "fizz",
        "foobar.h",
    ],
    headers_info = "@depend_on_what_you_use//src/aspect/support:toolchain_headers",
    toolchain = "@test_toolchain_rule_based//:toolchain",
)
