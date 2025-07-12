load("@rules_cc//cc/toolchains:tool.bzl", "cc_tool")
load("@rules_cc//cc/toolchains:tool_map.bzl", "cc_tool_map")
load("@rules_shell//shell:sh_binary.bzl", "sh_binary")

sh_binary(
    name = "noop",
    srcs = ["noop.sh"],
)

cc_tool(
    name = "noop_tool",
    src = ":noop",
)

# We need t register tools for compiling, as otherwise generating compilation commands returns empty results
cc_tool_map(
    name = "noop_tools",
    tools = {
        "@rules_cc//cc/toolchains/actions:c_compile": ":noop_tool",
        "@rules_cc//cc/toolchains/actions:cpp_compile_actions": ":noop_tool",
    },
    visibility = ["//:__pkg__"],
)
