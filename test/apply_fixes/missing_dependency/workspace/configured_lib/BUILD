load("@bazel_skylib//rules:common_settings.bzl", "bool_flag")

bool_flag(
    name = "custom_config",
    build_setting_default = False,
)

config_setting(
    name = "custom_config_active",
    flag_values = {":custom_config": "True"},
)

cc_library(
    name = "configured_deps",
    hdrs = ["configured_deps.h"],
    visibility = ["//visibility:public"],
    deps = select({
        ":custom_config_active": ["//ambiguous_lib:lib_a"],
        "//conditions:default": ["//ambiguous_lib:lib_b"],
    }),
)
