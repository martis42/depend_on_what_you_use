load("@rules_python//python:py_library.bzl", "py_library")

py_library(
    name = "release_prep",
    srcs = [
        "release_constants.py",
        "release_prep.py",
    ],
    imports = ["."],
    visibility = [":__subpackages__"],
)

py_library(
    name = "release_finalize",
    srcs = [
        "release_finalize.py",
        "release_github.py",
    ],
    imports = ["."],
    visibility = [":__subpackages__"],
    deps = [":release_prep"],
)
