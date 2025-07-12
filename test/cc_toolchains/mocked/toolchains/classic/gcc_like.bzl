load("@rules_cc//cc:cc_toolchain_config_lib.bzl", "tool_path")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/toolchains:cc_toolchain_config_info.bzl", "CcToolchainConfigInfo")

def _impl(ctx):
    return cc_common.create_cc_toolchain_config_info(
        ctx = ctx,
        features = [],
        cxx_builtin_include_directories = [],
        toolchain_identifier = "classic_toolchain_gcc_like",
        host_system_name = "local",
        target_system_name = "local",
        target_cpu = "k8",
        target_libc = "unknown",
        compiler = "gcc",
        abi_version = "unknown",
        abi_libc_version = "unknown",
        tool_paths = [
            tool_path(name = "ar", path = "not_used_in_test"),
            tool_path(name = "cpp", path = "not_used_in_test"),
            tool_path(name = "gcc", path = "tools/fake_gcc"),
            tool_path(name = "ld", path = "not_used_in_test"),
            tool_path(name = "nm", path = "not_used_in_test"),
            tool_path(name = "objdump", path = "not_used_in_test"),
            tool_path(name = "strip", path = "not_used_in_test"),
        ],
    )

cc_toolchain_config_gcc_like = rule(
    implementation = _impl,
    provides = [CcToolchainConfigInfo],
)
