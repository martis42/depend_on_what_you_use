load("@bazel_skylib//:workspace.bzl", "bazel_skylib_workspace")
load("@mypy_integration//repositories:deps.bzl", mypy_deps = "deps")
load("@mypy_integration//repositories:repositories.bzl", mypy_integration_dependencies = "repositories")
load("@rules_python//python:repositories.bzl", "python_register_multi_toolchains")

def dev_setup_step_2():
    """
    Perform the second development setup step.
    """
    bazel_skylib_workspace()
    mypy_deps("//third_party:mypy_requirements.txt")
    mypy_integration_dependencies()

    # Choose different version via: --@rules_python//python/config_settings:python_version=X
    python_register_multi_toolchains(
        name = "python",
        default_version = "3.10.9",
        python_versions = [
            "3.8.15",
            "3.9.16",
            "3.11.1",
        ],
    )
