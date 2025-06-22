# Do not waste memory by keeping idle Bazel servers around
startup --max_idle_secs=10

# Needless noise in the temporary workspaces
common --experimental_convenience_symlinks=ignore
common --lockfile_mode=off

# We are not interested in dependency resolution here
build --check_direct_dependencies=off

# Ensure only the hermetic toolchain is available to bazel
build:no_default_toolchain --incompatible_enable_cc_toolchain_resolution  # Can be dropped when Bazel 7 is the minimum version
build:no_default_toolchain --repo_env=BAZEL_DO_NOT_DETECT_CPP_TOOLCHAIN=1
build:no_default_toolchain --action_env=BAZEL_DO_NOT_DETECT_CPP_TOOLCHAIN=1

build:dwyu --aspects=//:aspect.bzl%dwyu
build:dwyu --output_groups=dwyu
