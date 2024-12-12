load("@rules_python//python:py_binary.bzl", "py_binary")
load(":create_tree_artifact.bzl", "create_tree_artifacts")

py_binary(
    name = "create_tree",
    srcs = ["create_tree.py"],
)

create_tree_artifacts(
    private_headers = "private_hdrs.h",
    public_headers = "public_hdrs.h",
    sources = "sources.cc",
)

cc_library(
    name = "transitive_dependency",
    hdrs = ["some_lib.h"],
)

cc_library(
    name = "intermediate_dependency",
    deps = [":transitive_dependency"],
)

cc_library(
    name = "tree_artifact_library",
    # DWYU requires header and source files being provided as separate tree artifacts. While Bazel somehow manages to
    # compile even if headers and sources are mixed into a single tree artifact, CcInfo.compilation_context won't be
    # filled correctly. This throws of DWYU, as it depends on the this information.
    srcs = [
        ":private_hdrs.h",
        ":sources.cc",
    ],
    hdrs = [":public_hdrs.h"],
    # We expect DWYU to detect the generated code using a dependency which is not declared as direct dependency
    deps = [":intermediate_dependency"],
)

cc_binary(
    name = "use_tree_artifact",
    srcs = ["use_tree_artifact.cpp"],
    deps = [":tree_artifact_library"],
)
