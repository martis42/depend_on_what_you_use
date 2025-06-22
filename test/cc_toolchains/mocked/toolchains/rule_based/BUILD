load("@rules_cc//cc/toolchains:toolchain.bzl", "cc_toolchain")
load("@rules_shell//shell:sh_binary.bzl", "sh_binary")

## The rule based approach is not setting 'tool_paths = ...' when using cc_common.create_cc_toolchain_config_info to construct CcToolchainConfigInfo.
## Although documentation on this case is sparse, it seems the default Bazel behavior when omitting 'tool_paths' is then to expect 'gcc' exists as binary at the root of the toolchain workspace.
## No matter if this is a gcc toolchain at all or not.
## Thus, one actually cannot freely define tools when using the rule_based CC toolchain approach, but is forced to follow this hidden contract.
sh_binary(
    name = "gcc_binary",
    srcs = ["gcc"],
    visibility = ["//visibility:public"],
)

##
## GCC like
##

cc_toolchain(
    name = "gcc_like_cc_toolchain",
    args = [],
    compiler = "gcc",
    tool_map = "//tools:compiler_tools",
)

toolchain(
    name = "gcc_like_toolchain",
    toolchain = ":gcc_like_cc_toolchain",
    toolchain_type = "@rules_cc//cc:toolchain_type",
    visibility = ["//visibility:public"],
)

##
## MSVC like
##

cc_toolchain(
    name = "msvc_like_cc_toolchain",
    args = ["//args:msvc_static_include_dirs"],
    compiler = "msvc",
    # Strictly speaking wrong as it points to a gcc tool, but the rule_based API enforces this naming and structure
    tool_map = "//tools:compiler_tools",
)

toolchain(
    name = "msvc_like_toolchain",
    toolchain = ":msvc_like_cc_toolchain",
    toolchain_type = "@rules_cc//cc:toolchain_type",
    visibility = ["//visibility:public"],
)

##
## Unknown compiler with defined builtin include directories
##

# Right now not possible due to bug in rules_cc preventing properly using relative paths for built_in include directories
# See https://github.com/bazelbuild/rules_cc/issues/277 and related issues
