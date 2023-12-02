load("@bazel_skylib//lib:versions.bzl", "versions")
load("@rules_python//python:pip.bzl", "pip_parse")

def setup_step_2():
    """
    Perform the second setup step.
    """

    # Strictly speaking we should use one pip_parse per Python version. However, pcpp has no transitive dependencies
    # and only a single wheel for all Python versions. Thus, we simply use a single resolved requirements file for all
    # Python versions.
    # Furthermore, this code is executed by the users of DWYU and we don't want to impose a specific Python interpreter
    # onto them.
    pip_parse(
        name = "dwyu_py_deps",
        requirements_lock = "@depend_on_what_you_use//third_party:requirements.txt",
    )

    # Fail early for incompatible Bazel versions instead of printing obscure errors from within our implementation
    versions.check(
        minimum_bazel_version = "5.4.0",
    )
