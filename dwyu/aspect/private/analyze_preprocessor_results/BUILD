load("@rules_python//python:defs.bzl", "py_binary")

# This pulls 'pcpp', although we are not using it. Preventing this would require restructuring the legacy Python implementation.
# Since, this target will either way just live temporarily, we accept this superfluous dependency.
# 'pcpp' is either way a small thing and chap to fetch.
py_binary(
    name = "main",
    srcs = [
        "lib.py",
        "main.py",
    ],
    # Compatibility to --noexperimental_python_import_all_repositories
    imports = ["../../../.."],
    visibility = ["//visibility:public"],
    deps = ["//dwyu/aspect/private/analyze_includes:lib"],
)
