load("@rules_cc//cc/toolchains:args.bzl", "cc_args")

cc_args(
    name = "msvc_static_include_dirs",
    actions = [
        "@rules_cc//cc/toolchains/actions:c_compile",
        "@rules_cc//cc/toolchains/actions:cpp_compile_actions",
    ],
    args = [
        "/I",
        "{include_dir_foobar}",
    ],
    data = [
        "//data:fizz",
        "//data:fizz_buzz",
        "//data:foobar",
    ],
    # This is a hack as it hard codes the toolchain repository name as implementation detail.
    # For now there is no way around this. Starting from rules_cc 1.3 one can use format variables with 'env'. But, one
    # cannot use more than one format variable per env var, which does not work out for constructing an env variable
    # pointing to multiple locations.
    env = select({
        "@platforms//os:windows": {"INCLUDE": "external/test_toolchain_rule_based+/data/fizz;external/test_toolchain_rule_based+/data/fizz/buzz"},
        "//conditions:default": {"INCLUDE": "external/test_toolchain_rule_based+/data/fizz:external/test_toolchain_rule_based+/data/fizz/buzz"},
    }),
    format = {
        "include_dir_foobar": "//data:foobar",
    },
    visibility = ["//:__pkg__"],
)
