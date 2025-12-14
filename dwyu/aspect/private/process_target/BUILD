load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_python//python:py_binary.bzl", "py_binary")

cc_binary(
    name = "main_cc",
    srcs = ["main.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
        "@nlohmann_json//:singleheader-json",
    ],
)

py_binary(
    name = "main_py",
    srcs = ["main.py"],
    main = "main.py",
    visibility = ["//visibility:public"],
)
