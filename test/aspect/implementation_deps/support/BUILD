load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "lib_with_defines",
    hdrs = ["lib_with_defines.h"],
    defines = ["THE_ANSWER=42"],
    visibility = ["//implementation_deps:__pkg__"],
    deps = [":transitive"],
)

cc_library(
    name = "lib_with_includes",
    hdrs = ["sub/dir/lib_with_includes.h"],
    includes = ["sub"],
    visibility = ["//implementation_deps:__pkg__"],
)

cc_library(
    name = "lib_with_strip_prefix",
    hdrs = ["sub/dir/lib_with_strip_prefix.h"],
    strip_include_prefix = "sub/dir",
    visibility = ["//implementation_deps:__pkg__"],
)

cc_library(
    name = "lib_with_add_prefix",
    hdrs = ["sub/dir/lib_with_add_prefix.h"],
    include_prefix = "some/prefix",
    visibility = ["//implementation_deps:__pkg__"],
)

cc_library(
    name = "transitive",
    hdrs = ["transitive.h"],
)
