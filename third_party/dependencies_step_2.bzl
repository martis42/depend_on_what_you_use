load("@rules_python//python:pip.bzl", "pip_parse")

def dependencies_step_2():
    pip_parse(
        name = "dwyu_py_deps",
        requirements_lock = "@depend_on_what_you_use//third_party:requirements.txt",
    )
