load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load(":executable_stub.bzl", "executable_stub")

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
    srcs = [
        "main.cpp",
        "preprocessing_hooks.h",
    ],
    visibility = ["//visibility:public"],
    deps = [
        ":preprocessing_hooks",
        "//dwyu/private:program_options",
        "//dwyu/private:utils",
        "@boost.wave//:wave",
        "@nlohmann_json//:json",
    ],
)
