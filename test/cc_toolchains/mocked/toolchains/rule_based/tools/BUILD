load("@rules_cc//cc/toolchains:tool.bzl", "cc_tool")
load("@rules_cc//cc/toolchains:tool_map.bzl", "cc_tool_map")

cc_tool(
    name = "fake_gcc",
    src = "//:gcc_binary",
    data = [
        "//data:fizz",
        "//data:fizz_buzz",
        "//data:foobar",
    ],
)

cc_tool_map(
    name = "compiler_tools",
    tools = {
        "@rules_cc//cc/toolchains/actions:c_compile": ":fake_gcc",
        "@rules_cc//cc/toolchains/actions:cpp_compile_actions": ":fake_gcc",
    },
    visibility = ["//:__pkg__"],
)
