load("@rules_cc//cc:cc_toolchain_config_lib.bzl", "tool_path")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/toolchains:cc_toolchain_config_info.bzl", "CcToolchainConfigInfo")

def _impl(ctx):
    irrelevant = "not_used_in_test"
    return cc_common.create_cc_toolchain_config_info(
        ctx = ctx,
        features = [],
        cxx_builtin_include_directories = [
            "data/fizz",
            "data/fizz/buzz",
            "data/foobar",
        ],
        toolchain_identifier = "unknown_with_built_in_dirs_toolchain_classic",
        host_system_name = "local",
        target_system_name = "local",
        target_cpu = "k8",
        target_libc = "unknown",
        compiler = "unknown",
        abi_version = "unknown",
        abi_libc_version = "unknown",
        tool_paths = [
            tool_path(name = "ar", path = irrelevant),
            tool_path(name = "cpp", path = irrelevant),
            tool_path(name = "gcc", path = "some/unknown/compiler"),
            tool_path(name = "ld", path = irrelevant),
            tool_path(name = "nm", path = irrelevant),
            tool_path(name = "objdump", path = irrelevant),
            tool_path(name = "strip", path = irrelevant),
        ],
    )

cc_toolchain_config_unknown_with_built_in_dirs = rule(
    implementation = _impl,
    provides = [CcToolchainConfigInfo],
)
