load("@rules_python//python:defs.bzl", "py_binary", "py_library")

py_binary(
    name = "analyze_many_includes",
    srcs = ["analyze_many_includes.py"],
    deps = ["//src/analyze_includes:lib"],
)

py_binary(
    name = "parsing_benchmark_many_files",
    srcs = ["parsing_benchmark_many_files.py"],
    deps = [":parsing_benchmark_lib"],
)

py_binary(
    name = "parsing_benchmark_many_macros",
    srcs = ["parsing_benchmark_many_macros.py"],
    deps = [":parsing_benchmark_lib"],
)

py_library(
    name = "parsing_benchmark_lib",
    srcs = ["parsing_benchmark_lib.py"],
    deps = ["//src/analyze_includes:lib"],
)
