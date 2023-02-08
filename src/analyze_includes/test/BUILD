load("@rules_python//python:defs.bzl", "py_test")

py_test(
    name = "evaluate_includes_test",
    srcs = ["evaluate_includes_test.py"],
    deps = ["//src/analyze_includes:lib"],
)

py_test(
    name = "parse_config_test",
    srcs = ["parse_config_test.py"],
    data = [
        "data/config/empty.json",
        "data/config/extra_ignore_paths.json",
        "data/config/ignore_patterns.json",
        "data/config/overwrite_default_ignore_paths.json",
    ],
    deps = ["//src/analyze_includes:lib"],
)

py_test(
    name = "parse_source_test",
    srcs = ["parse_source_test.py"],
    data = [
        "data/another_header.h",
        "data/commented_includes/block_comments.h",
        "data/commented_includes/mixed_style.h",
        "data/commented_includes/single_line_comments.h",
        "data/conditional_includes/if_def_style.h",
        "data/conditional_includes/if_defined_style.cc",
        "data/conditional_includes/if_value_style.h",
        "data/some_header.h",
    ],
    deps = ["//src/analyze_includes:lib"],
)

py_test(
    name = "system_under_inspection_test",
    srcs = ["system_under_inspection_test.py"],
    data = [
        "data/headers_info_empty.json",
        "data/headers_info_full.json",
    ],
    deps = ["//src/analyze_includes:lib"],
)
