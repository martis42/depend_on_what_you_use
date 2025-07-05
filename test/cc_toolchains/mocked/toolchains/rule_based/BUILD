load("@rules_cc//cc/toolchains:toolchain.bzl", "cc_toolchain")

# Stripped down to the essentials for include path testing.
# We are not testing builtin include directories, as the rule based CC toolchain does not offer a direct interface
# for this and the deduction of the built in paths based on args and tools is broken.
cc_toolchain(
    name = "test_toolchain",
    args = ["//args:toolchain_include_paths"],
    compiler = "gcc",
    tool_map = "//tools:noop_tools",
)

toolchain(
    name = "toolchain",
    toolchain = ":test_toolchain",
    toolchain_type = "@rules_cc//cc:toolchain_type",
    visibility = ["//visibility:public"],
)
