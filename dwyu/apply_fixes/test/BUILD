load("@rules_python//python:py_test.bzl", "py_test")
load(":hash_test.bzl", "hash_test_suite")

py_test(
    name = "apply_fixes_test",
    srcs = ["apply_fixes_test.py"],
    data = [
        "data/some_buildozer",
        "@buildozer_binary//:buildozer.exe",
    ],
    deps = [
        "//dwyu/apply_fixes:lib",
        "@rules_python//python/runfiles",
    ],
)

py_test(
    name = "bazel_query_test",
    srcs = ["bazel_query_test.py"],
    deps = ["//dwyu/apply_fixes:lib"],
)

py_test(
    name = "buildozer_executor_test",
    srcs = ["buildozer_executor_test.py"],
    deps = ["//dwyu/apply_fixes:lib"],
)

py_test(
    name = "cli_test",
    srcs = ["cli_test.py"],
    deps = ["//dwyu/apply_fixes:lib"],
)

py_test(
    name = "get_dwyu_reports_test",
    srcs = ["get_dwyu_reports_test.py"],
    data = [
        "data/gather_reports_search_path/not_a_report.txt",
        "data/gather_reports_search_path/root_target_dwyu_report.json",
        "data/gather_reports_search_path/sub/nested_target_dwyu_report.json",
    ],
    deps = [
        "//dwyu/apply_fixes:lib",
        "@rules_python//python/runfiles",
    ],
)

hash_test_suite(name = "hash_starlark_test")

py_test(
    name = "hash_python_test",
    srcs = ["hash_test.py"],
    main = "hash_test.py",
    deps = ["//dwyu/apply_fixes:lib"],
)

py_test(
    name = "search_missing_deps_test",
    srcs = ["search_missing_deps_test.py"],
    deps = ["//dwyu/apply_fixes:lib"],
)

py_test(
    name = "summary_test",
    srcs = ["summary_test.py"],
    deps = ["//dwyu/apply_fixes:lib"],
)

py_test(
    name = "utils_test",
    srcs = ["utils_test.py"],
    deps = ["//dwyu/apply_fixes:lib"],
)
