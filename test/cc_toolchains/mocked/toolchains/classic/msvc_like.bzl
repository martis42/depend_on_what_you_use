load("@bazel_skylib//lib:paths.bzl", "paths")
load("@rules_cc//cc:action_names.bzl", "ALL_CC_COMPILE_ACTION_NAMES")
load("@rules_cc//cc:cc_toolchain_config_lib.bzl", "env_entry", "env_set", "feature", "flag_group", "flag_set", "tool_path")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/toolchains:cc_toolchain_config_info.bzl", "CcToolchainConfigInfo")

def _impl(ctx):
    INCLUDE_VAR = paths.join(ctx.label.workspace_root, "data/fizz") + ctx.configuration.host_path_separator + paths.join(ctx.label.workspace_root, "data/fizz/buzz")
    features = [
        feature(
            name = "msvc_compile_env",
            enabled = True,
            env_sets = [
                env_set(
                    actions = ALL_CC_COMPILE_ACTION_NAMES,
                    env_entries = [env_entry(key = "INCLUDE", value = INCLUDE_VAR)],
                ),
            ],
        ),
        feature(
            name = "msvc_static_include_dirs",
            enabled = True,
            flag_sets = [
                flag_set(
                    actions = ALL_CC_COMPILE_ACTION_NAMES,
                    flag_groups = ([flag_group(flags = ["/I", paths.join(ctx.label.workspace_root, "data/foobar")])]),
                ),
            ],
        ),
    ]

    irrelevant = "not_used_in_test"
    return cc_common.create_cc_toolchain_config_info(
        ctx = ctx,
        features = features,
        cxx_builtin_include_directories = [],
        toolchain_identifier = "msvc_like_cc_toolchain_classic",
        host_system_name = "local",
        target_system_name = "local",
        target_cpu = "k8",
        target_libc = "unknown",
        compiler = "msvc",
        abi_version = "unknown",
        abi_libc_version = "unknown",
        tool_paths = [
            tool_path(name = "ar", path = irrelevant),
            tool_path(name = "cpp", path = irrelevant),
            tool_path(name = "gcc", path = "some/msvc"),
            tool_path(name = "ld", path = irrelevant),
            tool_path(name = "nm", path = irrelevant),
            tool_path(name = "objdump", path = irrelevant),
            tool_path(name = "strip", path = irrelevant),
        ],
    )

cc_toolchain_config_msvc_like = rule(
    implementation = _impl,
    provides = [CcToolchainConfigInfo],
)
