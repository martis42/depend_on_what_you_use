load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_python//python:py_binary.bzl", "py_binary")
load("@rules_python//python:py_library.bzl", "py_library")

package(
    default_visibility = [":__subpackages__"],
)

py_library(
    name = "lib",
    srcs = [
        "evaluate_includes.py",
        "parse_config.py",
        "parse_source.py",
        "result.py",
        "std_header.py",
        "system_under_inspection.py",
    ],
    visibility = ["//dwyu/aspect/private:__subpackages__"],
    deps = ["@dwyu_pcpp//:pcpp"],
)

py_binary(
    name = "analyze_includes",
    srcs = ["main.py"],
    # Compatibility to --noexperimental_python_import_all_repositories
    imports = ["../../../.."],
    legacy_create_init = False,
    main = "main.py",
    visibility = ["//visibility:public"],
    deps = [":lib"],
)

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        ":evaluate_includes",
        ":include_statement",
        ":result",
        ":system_under_inspection",
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
    ],
)

cc_library(
    name = "evaluate_includes",
    srcs = ["evaluate_includes.cpp"],
    hdrs = ["evaluate_includes.h"],
    deps = [
        ":include_statement",
        ":result",
        ":system_under_inspection",
    ],
)

cc_library(
    name = "include_statement",
    srcs = ["include_statement.cpp"],
    hdrs = ["include_statement.h"],
    deps = ["@nlohmann_json//:singleheader-json"],
)

cc_library(
    name = "result",
    srcs = ["result.cpp"],
    hdrs = ["result.h"],
    deps = [
        ":include_statement",
        "@nlohmann_json//:singleheader-json",
    ],
)

cc_library(
    name = "system_under_inspection",
    srcs = ["system_under_inspection.cpp"],
    hdrs = ["system_under_inspection.h"],
    deps = ["@nlohmann_json//:singleheader-json"],
)
