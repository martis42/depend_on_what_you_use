load("@bazel_skylib//:workspace.bzl", "bazel_skylib_workspace")
load("@mypy_integration//repositories:repositories.bzl", mypy_integration_repositories = "repositories")
load("@rules_python//python:pip.bzl", "pip_parse")
load("@rules_python//python:repositories.bzl", "python_register_multi_toolchains")

def dev_setup_step_2():
    """
    Perform the second development setup step.
    """
    bazel_skylib_workspace()

    mypy_integration_repositories()

    pip_parse(
        name = "dwyu_mypy_deps",
        requirements_lock = "//third_party:mypy_requirements.txt",
    )

    # Choose different version via: --@rules_python//python/config_settings:python_version=X
    python_register_multi_toolchains(
        name = "python",
        default_version = "3.10",
        python_versions = [
            "3.8",
            "3.9",
            "3.11",
        ],
    )
