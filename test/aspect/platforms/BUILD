load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "linux",
    srcs = ["linux.cpp"],
    target_compatible_with = ["@platforms//os:linux"],
)

cc_library(
    name = "windows",
    srcs = ["windows.cpp"],
    target_compatible_with = ["@platforms//os:windows"],
)

cc_binary(
    name = "use_linux",
    srcs = ["main.cpp"],
    deps = [":linux"],
)

cc_binary(
    name = "use_windows",
    srcs = ["main.cpp"],
    deps = [":windows"],
)
