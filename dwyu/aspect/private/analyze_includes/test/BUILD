load("@rules_cc//cc:cc_test.bzl", "cc_test")
load("@rules_python//python:py_test.bzl", "py_test")

py_test(
    name = "evaluate_includes_test",
    srcs = ["evaluate_includes_test.py"],
    deps = ["//dwyu/aspect/private/analyze_includes:lib"],
)

py_test(
    name = "parse_config_test",
    srcs = ["parse_config_test.py"],
    data = [
        "data/config/empty.json",
        "data/config/extra_ignore_paths.json",
        "data/config/ignore_patterns.json",
        "data/config/overwrite_default_ignore_paths.json",
        "data/config/system_headers_info.json",
    ],
    deps = ["//dwyu/aspect/private/analyze_includes:lib"],
)

py_test(
    name = "parse_source_test",
    srcs = ["parse_source_test.py"],
    data = [
        "data/another_header.h",
        "data/commented_includes/block_comments.h",
        "data/commented_includes/mixed_style.h",
        "data/commented_includes/single_line_comments.h",
        "data/empty_header.h",
        "data/header_with_defines.h",
        "data/include_based_on_pre_processor_token.h",
        "data/some_defines.h",
        "data/some_header.h",
        "data/use_defines.h",
    ],
    deps = ["//dwyu/aspect/private/analyze_includes:lib"],
)

py_test(
    name = "result_test",
    srcs = ["result_test.py"],
    deps = ["//dwyu/aspect/private/analyze_includes:lib"],
)

py_test(
    name = "system_under_inspection_test",
    srcs = ["system_under_inspection_test.py"],
    data = [
        "data/dep_info_bar.json",
        "data/dep_info_foo.json",
        "data/implementation_dep_info_bar.json",
        "data/implementation_dep_info_foo.json",
        "data/target_under_inspection.json",
        "data/target_under_inspection_empty.json",
    ],
    deps = ["//dwyu/aspect/private/analyze_includes:lib"],
)

cc_test(
    name = "evaluate_includes_test_cc",
    srcs = ["evaluate_includes_test.cpp"],
    deps = [
        "//dwyu/aspect/private/analyze_includes:evaluate_includes",
        "//dwyu/aspect/private/analyze_includes:include_statement",
        "//dwyu/aspect/private/analyze_includes:system_under_inspection",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
        "@nlohmann_json//:singleheader-json",
    ],
)

cc_test(
    name = "ignored_includes_test_cc",
    srcs = ["ignored_includes_test.cpp"],
    data = [
        "data/cc/ignored_includes.json",
        "data/cc/ignored_includes_empty.json",
    ],
    deps = [
        "//dwyu/aspect/private/analyze_includes:ignored_includes",
        "@boost//:regex",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)

cc_test(
    name = "include_statement_test",
    srcs = ["include_statement_test.cpp"],
    data = [
        "data/cc/preprocessed_file_empty.json",
        "data/cc/preprocessed_file_without_includes.json",
        "data/cc/preprocessed_files_with_includes.json",
    ],
    deps = [
        "//dwyu/aspect/private/analyze_includes:ignored_includes",
        "//dwyu/aspect/private/analyze_includes:include_statement",
        "@boost//:regex",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)

cc_test(
    name = "result_test_cc",
    srcs = ["result_test.cpp"],
    deps = [
        "//dwyu/aspect/private/analyze_includes:include_statement",
        "//dwyu/aspect/private/analyze_includes:result",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
        "@nlohmann_json//:singleheader-json",
    ],
)

cc_test(
    name = "system_under_inspection_test_cc",
    srcs = ["system_under_inspection_test.cpp"],
    data = [
        "data/cc/dep_info_duplicate_header_a.json",
        "data/cc/dep_info_duplicate_header_b.json",
        "data/cc/dep_info_foo.json",
        "data/cc/dep_info_foobar.json",
        "data/cc/dep_info_no_headers.json",
        "data/cc/impl_dep_info_buzz.json",
        "data/cc/impl_dep_info_fizz.json",
        "data/cc/target_under_inspection.json",
        "data/cc/target_under_inspection_no_headers.json",
    ],
    deps = [
        "//dwyu/aspect/private/analyze_includes:system_under_inspection",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)

cc_test(
    name = "utility_test",
    srcs = ["utility_test.cpp"],
    data = ["data/cc/target_under_inspection.json"],
    deps = [
        "//dwyu/aspect/private/analyze_includes:utility",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)
