load("@dwyu_mypy_deps//:requirements.bzl", install_mypy_deps = "install_deps")

def dev_setup_step_3():
    """
    Perform the third development setup step.
    """
    install_mypy_deps()
