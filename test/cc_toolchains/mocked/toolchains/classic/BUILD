load("@rules_cc//cc/toolchains:cc_toolchain.bzl", "cc_toolchain")
load(":config.bzl", "cc_toolchain_config")

filegroup(name = "empty")

filegroup(
    name = "toolchain_headers",
    srcs = glob(["data/**"]),
)

cc_toolchain_config(name = "toolchain_config")

# Stripped down to the essentials for include path testing
cc_toolchain(
    name = "test_toolchain",
    all_files = ":toolchain_headers",
    compiler_files = ":empty",
    dwp_files = ":empty",
    linker_files = ":empty",
    objcopy_files = ":empty",
    strip_files = ":empty",
    supports_param_files = False,
    toolchain_config = ":toolchain_config",
    toolchain_identifier = "linux_test_toolchain",
)

toolchain(
    name = "toolchain",
    toolchain = ":test_toolchain",
    toolchain_type = "@rules_cc//cc:toolchain_type",
)
