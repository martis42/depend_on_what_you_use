load("@dwyu_mypy_deps//:requirements.bzl", "requirement")
load("@rules_python//python:pip.bzl", "compile_pip_requirements")

alias(
    name = "mypy",
    actual = requirement("mypy"),
    visibility = ["//:__pkg__"],
)

compile_pip_requirements(
    name = "mypy_requirements",
    src = "mypy_requirements.in",
    requirements_txt = "mypy_requirements.txt",
)
