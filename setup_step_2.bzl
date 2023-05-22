load("@bazel_skylib//lib:versions.bzl", "versions")
load("@rules_python//python:pip.bzl", "pip_parse")

def setup_step_2():
    """
    Perform the second setup step.
    """
    pip_parse(
        name = "dwyu_py_deps",
        requirements_lock = "@depend_on_what_you_use//third_party:requirements.txt",
    )

    # Fail early for incompatible Bazel versions instead of printing obscure errors from within our implementation
    versions.check(
        minimum_bazel_version = "5.0.0",
    )
