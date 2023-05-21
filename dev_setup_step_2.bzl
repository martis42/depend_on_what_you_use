load("@bazel_skylib//:workspace.bzl", "bazel_skylib_workspace")
load("@mypy_integration//repositories:deps.bzl", mypy_deps = "deps")
load("@mypy_integration//repositories:repositories.bzl", mypy_integration_dependencies = "repositories")

def dev_setup_step_2():
    """
    Perform the second development setup step.
    """
    bazel_skylib_workspace()
    mypy_deps("//third_party:mypy_requirements.txt")
    mypy_integration_dependencies()
