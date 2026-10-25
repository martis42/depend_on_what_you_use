load("@rules_python//python:py_library.bzl", "py_library")

py_library(
    name = "release_constants",
    srcs = ["release_constants.py"],
    imports = ["."],
)

py_library(
    name = "release_finalize",
    srcs = ["release_finalize.py"],
    imports = ["."],
    visibility = [":__subpackages__"],
    deps = [
        ":release_constants",
        ":release_github",
    ],
)

py_library(
    name = "release_github",
    srcs = ["release_github.py"],
    imports = ["."],
    visibility = [":__subpackages__"],
    deps = [":release_constants"],
)

py_library(
    name = "release_prep",
    srcs = ["release_prep.py"],
    imports = ["."],
    visibility = [":__subpackages__"],
    deps = [
        ":release_constants",
        ":release_github",
    ],
)

py_library(
    name = "release_publish",
    srcs = ["release_publish.py"],
    imports = ["."],
    visibility = [":__subpackages__"],
    deps = [
        ":release_constants",
        ":release_github",
    ],
)

py_library(
    name = "release_ready_bcr_pr",
    srcs = ["release_ready_bcr_pr.py"],
    imports = ["."],
    visibility = [":__subpackages__"],
    deps = [":release_github"],
)
