load("@rules_python//python:pip.bzl", "pip_parse")

def setup_step_3():
    """
    Perform the third setup step.
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
