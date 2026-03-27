load("@rules_cc//cc:cc_test.bzl", "cc_test")

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
        "data/ignored_includes.json",
        "data/ignored_includes_empty.json",
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
        "data/preprocessed_file_empty.json",
        "data/preprocessed_file_without_includes.json",
        "data/preprocessed_files_with_includes.json",
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
        "data/dep_info_duplicate_header_a.json",
        "data/dep_info_duplicate_header_b.json",
        "data/dep_info_foo.json",
        "data/dep_info_foobar.json",
        "data/dep_info_no_headers.json",
        "data/impl_dep_info_buzz.json",
        "data/impl_dep_info_fizz.json",
        "data/target_under_inspection.json",
        "data/target_under_inspection_no_headers.json",
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
    data = ["data/target_under_inspection.json"],
    deps = [
        "//dwyu/aspect/private/analyze_includes:utility",
        "@googletest//:gtest",
        "@googletest//:gtest_main",
    ],
)
