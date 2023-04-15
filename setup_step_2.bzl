load("@bazel_skylib//:workspace.bzl", "bazel_skylib_workspace")
load("@bazel_skylib//lib:versions.bzl", "versions")
load("//third_party:dependencies_step_2.bzl", "dependencies_step_2")

def setup_step_2():
    """
    Perform the second setup step.
    """
    dependencies_step_2()

    # Fail early for incompatible Bazel versions instead of printing obscure errors from within our implementation
    versions.check(
        minimum_bazel_version = "4.0.0",
    )

def dev_setup_step_2():
    """
    Setup step required for development but of not interest for users.
    """
    bazel_skylib_workspace()
