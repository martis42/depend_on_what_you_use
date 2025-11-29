load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load(":executable_stub.bzl", "executable_stub")

cc_library(
    name = "extract_includes",
    srcs = ["extract_includes.cpp"],
    hdrs = ["extract_includes.h"],
    visibility = [":__subpackages__"],
)

cc_library(
    name = "preprocessing_hooks",
    hdrs = ["preprocessing_hooks.h"],
    visibility = [":__subpackages__"],
    deps = ["@boost.wave//:wave"],
)

# This target exists so the legacy Python implementation can be used without a user having to depend on boost,
# although he is not even using the new C++ based implementation.
executable_stub(
    name = "stub",
    visibility = ["//visibility:public"],
)

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        ":preprocessing_hooks",
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
        "@boost.wave//:wave",
        "@nlohmann_json//:json",
    ],
)

cc_binary(
    name = "main_no_preprocessing",
    srcs = ["main_no_preprocessing.cpp"],
    visibility = ["//visibility:public"],
    deps = [
        ":extract_includes",
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
        "@nlohmann_json//:json",
    ],
)
