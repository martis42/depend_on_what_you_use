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
