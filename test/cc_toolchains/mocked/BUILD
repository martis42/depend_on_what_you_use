load(
    ":toolchain_headers_info_test.bzl",
    "classic_gcc_like_headers_info_test",
    "classic_msvc_like_headers_info_test",
    "classic_unknown_with_built_in_dirs_headers_info_test",
    "rule_based_gcc_like_headers_info_test",
    "rule_based_msvc_like_headers_info_test",
)

EXPECTED_INCLUDE_STATEMENTS = [
    "buzz.h",
    "buzz/buzz.h",
    "fizz",
    "foobar.h",
]

EXPECTED_CLASSIC_TOOLCHAIN_HEADER_FILES = [
    "external/test_toolchain_classic+/data/fizz/fizz",
    "external/test_toolchain_classic+/data/fizz/buzz/buzz.h",
    "external/test_toolchain_classic+/data/foobar/foobar.h",
]

EXPECTED_RULE_BASED_TOOLCHAIN_HEADER_FILES = [
    "external/test_toolchain_rule_based+/data/fizz/fizz",
    "external/test_toolchain_rule_based+/data/fizz/buzz/buzz.h",
    "external/test_toolchain_rule_based+/data/foobar/foobar.h",
]

classic_gcc_like_headers_info_test(
    name = "classic_gcc_like_headers_info_test",
    expected_header_files = EXPECTED_CLASSIC_TOOLCHAIN_HEADER_FILES,
    expected_include_statements = EXPECTED_INCLUDE_STATEMENTS,
    headers_info = "@depend_on_what_you_use//dwyu/aspect/private:cc_toolchain_headers",
)

classic_msvc_like_headers_info_test(
    name = "classic_msvc_like_headers_info_test",
    expected_header_files = EXPECTED_CLASSIC_TOOLCHAIN_HEADER_FILES,
    expected_include_statements = EXPECTED_INCLUDE_STATEMENTS,
    headers_info = "@depend_on_what_you_use//dwyu/aspect/private:cc_toolchain_headers",
)

classic_unknown_with_built_in_dirs_headers_info_test(
    name = "classic_unknown_with_built_in_dirs_headers_info_test",
    expected_header_files = EXPECTED_CLASSIC_TOOLCHAIN_HEADER_FILES,
    expected_include_statements = EXPECTED_INCLUDE_STATEMENTS,
    headers_info = "@depend_on_what_you_use//dwyu/aspect/private:cc_toolchain_headers",
)

rule_based_gcc_like_headers_info_test(
    name = "rule_based_gcc_like_headers_info_test",
    expected_header_files = EXPECTED_RULE_BASED_TOOLCHAIN_HEADER_FILES,
    expected_include_statements = EXPECTED_INCLUDE_STATEMENTS,
    headers_info = "@depend_on_what_you_use//dwyu/aspect/private:cc_toolchain_headers",
)

rule_based_msvc_like_headers_info_test(
    name = "rule_based_msvc_like_headers_info_test",
    expected_header_files = EXPECTED_RULE_BASED_TOOLCHAIN_HEADER_FILES,
    expected_include_statements = EXPECTED_INCLUDE_STATEMENTS,
    headers_info = "@depend_on_what_you_use//dwyu/aspect/private:cc_toolchain_headers",
)
