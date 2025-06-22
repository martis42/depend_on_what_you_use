load("@rules_cc//cc/toolchains:args.bzl", "cc_args")

cc_args(
    name = "toolchain_include_paths",
    actions = [
        "@rules_cc//cc/toolchains/actions:c_compile",
        "@rules_cc//cc/toolchains/actions:cpp_compile_actions",
    ],
    args = [
        "-I",
        "{include_dir_fizz}",
        "-iquote",
        "{include_dir_fizz_buzz}",
        "-isystem",
        "{include_dir_foobar}",
    ],
    data = [
        "//data:fizz",
        "//data:fizz_buzz",
        "//data:foobar",
    ],
    format = {
        "include_dir_fizz": "//data:fizz",
        "include_dir_fizz_buzz": "//data:fizz_buzz",
        "include_dir_foobar": "//data:foobar",
    },
    visibility = ["//:__pkg__"],
)
