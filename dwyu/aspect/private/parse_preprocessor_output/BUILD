load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_python//python:defs.bzl", "py_binary")

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        "@boost.algorithm",
        "@boost.filesystem",
        "@boost.program_options",
    ],
)

py_binary(
    name = "main_py",
    srcs = ["main.py"],
    # Compatibility to --noexperimental_python_import_all_repositories
    imports = ["../../../.."],
    legacy_create_init = False,
    main = "main.py",
    visibility = ["//visibility:public"],
    # deps = [
    #     ":lib",
    #     "//dwyu/aspect/private/analyze_includes:lib",
    # ],
)
