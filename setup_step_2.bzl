load("@bazel_skylib//lib:versions.bzl", "versions")
load("//third_party:dependencies_step_2.bzl", "dependencies_step_2")

def setup_step_2():
    """
    Perform the second setup step.
    """
    dependencies_step_2()

    # Fail early for incompatible Bazel versions instead of printing obscure errors from within our implementation
    versions.check(
        minimum_bazel_version = "5.0.0",
    )
