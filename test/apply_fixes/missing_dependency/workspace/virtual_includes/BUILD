load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "includes",
    hdrs = ["includes.h"],
    includes = ["."],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "include_prefix",
    hdrs = [
        "virtual_1.h",
        "virtual_2.h",
    ],
    include_prefix = "foo/bar",
    visibility = ["//visibility:public"],
)

cc_library(
    name = "strip_include_prefix",
    hdrs = [
        "sub/sub_1.h",
        "sub/sub_2.h",
    ],
    strip_include_prefix = "sub",
    visibility = ["//visibility:public"],
)

cc_library(
    name = "prefixed_and_stripped",
    hdrs = ["sub/sub_3.h"],
    include_prefix = "foo/bar",
    strip_include_prefix = "sub",
    visibility = ["//visibility:public"],
)

# The workspace root is 'test/apply_fixes/', thus this is the repository-relative (leading '/') spelling of the
# package-relative 'sub' prefix used above.
cc_library(
    name = "absolute_strip_include_prefix",
    hdrs = ["sub/sub_4.h"],
    strip_include_prefix = "/missing_dependency/workspace/virtual_includes/sub",
    visibility = ["//visibility:public"],
)

cc_library(
    name = "absolute_prefixed_and_stripped",
    hdrs = ["sub/sub_5.h"],
    include_prefix = "foo/bar",
    strip_include_prefix = "/missing_dependency/workspace/virtual_includes/sub",
    visibility = ["//visibility:public"],
)
