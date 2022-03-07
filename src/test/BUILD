load("@rules_python//python:defs.bzl", "py_test")

py_test(
    name = "evaluate_includes_test",
    srcs = ["evaluate_includes_test.py"],
    deps = ["//src:lib"],
)

py_test(
    name = "get_dependencies_test",
    srcs = ["get_dependencies_test.py"],
    data = [
        "data/deps_info_empty.json",
        "data/deps_info_full.json",
    ],
    deps = ["//src:lib"],
)

py_test(
    name = "parse_config_test",
    srcs = ["parse_config_test.py"],
    data = [
        "data/config.json",
        "data/config_empty.json",
    ],
    deps = ["//src:lib"],
)

py_test(
    name = "parse_source_test",
    srcs = ["parse_source_test.py"],
    data = [
        "data/another_header.h",
        "data/commented_includes/block_comments.h",
        "data/commented_includes/mixed_style.h",
        "data/commented_includes/single_line_comments.h",
        "data/some_header.h",
    ],
    deps = ["//src:lib"],
)
