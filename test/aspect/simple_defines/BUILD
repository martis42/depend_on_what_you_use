load("@bazel_skylib//rules:common_settings.bzl", "bool_flag")
load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library")
load(":defs.bzl", "if_foo")

bool_flag(
    name = "enable_foo",
    build_setting_default = False,
)

config_setting(
    name = "foo_enabled",
    flag_values = {":enable_foo": "True"},
)

cc_library(
    name = "foo",
    srcs = ["foo.cc"],
    hdrs = ["foo.h"],
)

cc_library(
    name = "bar",
    srcs = ["bar.cc"],
    hdrs = ["bar.h"],
)

cc_binary(
    name = "use_foo_or_bar",
    srcs = ["main.cc"],
    defines = if_foo(["FOO"]),
    deps = if_foo(
        [":foo"],
        [":bar"],
    ),
)
