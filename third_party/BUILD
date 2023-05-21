load("@rules_python//python:pip.bzl", "compile_pip_requirements")

compile_pip_requirements(
    name = "requirements",
    extra_args = ["--resolver=backtracking"],
    requirements_in = "requirements.in",
    requirements_txt = "requirements.txt",
)

compile_pip_requirements(
    name = "mypy_requirements",
    extra_args = ["--resolver=backtracking"],
    requirements_in = "mypy_requirements.in",
    requirements_txt = "mypy_requirements.txt",
)
