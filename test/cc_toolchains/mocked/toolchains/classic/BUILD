load("@rules_cc//cc/toolchains:cc_toolchain.bzl", "cc_toolchain")
load(":gcc_like.bzl", "cc_toolchain_config_gcc_like")
load(":msvc_like.bzl", "cc_toolchain_config_msvc_like")
load(":unknown_with_built_in_dirs.bzl", "cc_toolchain_config_unknown_with_built_in_dirs")

filegroup(
    name = "empty",
)

filegroup(
    name = "headers",
    srcs = glob(["data/**"]),
)

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
    toolchain_identifier = "gcc_like_toolchain_classic",
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
    toolchain_identifier = "msvc_like_cc_toolchain_classic",
)

toolchain(
    name = "msvc_like_toolchain",
    toolchain = ":msvc_like_cc_toolchain",
    toolchain_type = "@rules_cc//cc:toolchain_type",
)

##
## Unknown compiler with defined builtin include directories
##

cc_toolchain_config_unknown_with_built_in_dirs(
    name = "unknown_with_built_in_dirs_config",
)

cc_toolchain(
    name = "unknown_with_built_in_dirs_cc_toolchain",
    all_files = ":headers",
    compiler_files = ":empty",
    dwp_files = ":empty",
    linker_files = ":empty",
    objcopy_files = ":empty",
    strip_files = ":empty",
    supports_param_files = False,
    toolchain_config = ":unknown_with_built_in_dirs_config",
    toolchain_identifier = "unknown_with_built_in_dirs_toolchain_classic",
)

toolchain(
    name = "unknown_with_built_in_dirs_toolchain",
    toolchain = ":unknown_with_built_in_dirs_cc_toolchain",
    toolchain_type = "@rules_cc//cc:toolchain_type",
)
