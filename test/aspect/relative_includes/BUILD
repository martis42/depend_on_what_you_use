load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "normal_include",
    srcs = [
        "normal_include.cpp",
        "some/sub/dir2/baz.h",
    ],
    hdrs = [
        "normal_include.h",
        "some/sub/dir/bar.h",
        "some/sub/dir/foo.h",
    ],
)

cc_library(
    name = "system_include",
    srcs = [
        "some/sub/dir2/baz.h",
        "system_include.cpp",
    ],
    hdrs = [
        "some/sub/dir/bar.h",
        "some/sub/dir/foo.h",
        "system_include.h",
    ],
    includes = ["some"],
)

cc_library(
    name = "virtual_strip",
    srcs = [
        "other/other.h",
        "virtual_strip.cpp",
    ],
    hdrs = [
        "some/sub/dir/bar.h",
        "some/sub/dir/foo.h",
        "some/sub/dir2/baz.h",
        "some/virtual_strip.h",
    ],
    strip_include_prefix = "some",
)

cc_library(
    name = "virtual_prefix",
    srcs = [
        "other/other.h",
        "virtual_prefix.cpp",
    ],
    hdrs = [
        "some/sub/dir/bar.h",
        "some/sub/dir/foo.h",
        "some/sub/dir2/baz.h",
        "virtual_prefix.h",
    ],
    include_prefix = "custom/prefix",
)

cc_binary(
    name = "use_normal_include",
    srcs = ["use_normal_include.cpp"],
    deps = [":normal_include"],
)

cc_binary(
    name = "use_system_include",
    srcs = ["use_system_include.cpp"],
    deps = [":system_include"],
)

cc_binary(
    name = "use_virtual_prefix",
    srcs = ["use_virtual_prefix.cpp"],
    deps = [":virtual_prefix"],
)

cc_binary(
    name = "use_virtual_strip",
    srcs = ["use_virtual_strip.cpp"],
    deps = [":virtual_strip"],
)
