load("@rules_cc//cc/toolchains:cc_toolchain.bzl", "cc_toolchain")
load(":gcc_like.bzl", "cc_toolchain_config_gcc_like")
load(":msvc_like.bzl", "cc_toolchain_config_msvc_like")

filegroup(
    name = "empty",
)

filegroup(
    name = "headers",
    srcs = glob(["data/**"]),
)

# cc_toolchain_config(name = "toolchain_config")

# # Stripped down to the essentials for include path testing
# cc_toolchain(
#     name = "test_toolchain",
#     all_files = ":all_files",
#     compiler_files = ":empty",
#     dwp_files = ":empty",
#     linker_files = ":empty",
#     objcopy_files = ":empty",
#     strip_files = ":empty",
#     supports_param_files = False,
#     toolchain_config = ":toolchain_config",
#     toolchain_identifier = "linux_test_toolchain",
# )

# toolchain(
#     name = "toolchain",
#     toolchain = ":test_toolchain",
#     toolchain_type = "@rules_cc//cc:toolchain_type",
# )

##
## GCC like
##

filegroup(
    name = "gcc_like_compiler_files",
    srcs = ["tools/fake_gcc"],
)

filegroup(
    name = "gcc_like_all_files",
    srcs = [
        ":gcc_like_compiler_files",
        ":headers",
    ],
)

cc_toolchain_config_gcc_like(
    name = "gcc_like_toolchain_config",
)

cc_toolchain(
    name = "gcc_like_cc_toolchain",
    all_files = ":gcc_like_all_files",
    compiler_files = ":gcc_like_compiler_files",
    dwp_files = ":empty",
    linker_files = ":empty",
    objcopy_files = ":empty",
    strip_files = ":empty",
    supports_param_files = False,
    toolchain_config = ":gcc_like_toolchain_config",
    toolchain_identifier = "gcc_like_cc_toolchain",
)

toolchain(
    name = "gcc_like_toolchain",
    toolchain = ":gcc_like_cc_toolchain",
    toolchain_type = "@rules_cc//cc:toolchain_type",
)

##
## MSVC like
##

cc_toolchain_config_msvc_like(
    name = "msvc_like_toolchain_config",
)

cc_toolchain(
    name = "msvc_like_cc_toolchain",
    all_files = ":headers",
    compiler_files = ":empty",
    dwp_files = ":empty",
    linker_files = ":empty",
    objcopy_files = ":empty",
    strip_files = ":empty",
    supports_param_files = False,
    toolchain_config = ":msvc_like_toolchain_config",
    toolchain_identifier = "msvc_like_cc_toolchain",
)

toolchain(
    name = "msvc_like_toolchain",
    toolchain = ":msvc_like_cc_toolchain",
    toolchain_type = "@rules_cc//cc:toolchain_type",
)
