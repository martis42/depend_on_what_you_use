load("@bazel_skylib//lib:paths.bzl", "paths")
load("@rules_cc//cc:action_names.bzl", "ALL_CC_COMPILE_ACTION_NAMES")
load("@rules_cc//cc:cc_toolchain_config_lib.bzl", "feature", "flag_group", "flag_set")
load("@rules_cc//cc/common:cc_common.bzl", "cc_common")
load("@rules_cc//cc/toolchains:cc_toolchain_config_info.bzl", "CcToolchainConfigInfo")

def _impl(ctx):
    features = [
        feature(
            name = "add_static_includes",
            enabled = True,
            flag_sets = [
                flag_set(
                    actions = ALL_CC_COMPILE_ACTION_NAMES,
                    flag_groups = ([
                        flag_group(
                            flags = [
                                "-I",
                                paths.join(ctx.label.workspace_root, "data/toolchain_path/fizz"),
                                # By providing a sub dir of an already specified dir we can test that we report the multiple possible paths to a single header
                                "-iquote",
                                paths.join(ctx.label.workspace_root, "data/toolchain_path/fizz/buzz"),
                                "-isystem",
                                paths.join(ctx.label.workspace_root, "data/toolchain_path/foobar"),
                            ],
                        ),
                    ]),
                ),
            ],
        ),
    ]

    return cc_common.create_cc_toolchain_config_info(
        ctx = ctx,
        features = features,
        # Typically this is used to point to non hermetic system paths.
        # We point to a location in the hermetic toolchain files to make this test portable and the results deterministic.
        # Our code searches recursively below those directories and does not care if it searches in a system location or the bazel sandbox.
        # Note, relative paths have to be specified relative to where the toolchain config is being instantiated.
        cxx_builtin_include_directories = [
            "data/system_path",
            # By providing a sub dir of an already specified dir we can test that we report the multiple possible paths to a single header
            "data/system_path/tik",
        ],
        toolchain_identifier = "test_toolchain",
        host_system_name = "local",
        target_system_name = "local",
        target_cpu = "k8",
        target_libc = "unknown",
        compiler = "clang",
        abi_version = "unknown",
        abi_libc_version = "unknown",
        tool_paths = [],  # irrelevant for our tests
    )

cc_toolchain_config = rule(
    implementation = _impl,
    provides = [CcToolchainConfigInfo],
)
