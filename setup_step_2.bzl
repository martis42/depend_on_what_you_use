load("@bazel_skylib//lib:versions.bzl", "versions")
load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")
load("@rules_python//python:repositories.bzl", "py_repositories")

def setup_step_2():
    """
    Perform the second setup step.
    """

    # Fail early for incompatible Bazel versions instead of printing obscure errors from within our implementation
    versions.check(
        # Keep in sync with MODULE.bazel, .bcr/presubmit.yml and the README.md
        minimum_bazel_version = "6.0.0",
    )

    py_repositories()

    # We need to manage protobuf in the legacy WORKSPACE setup as rules_cc does not manage it properly itself
    protobuf_deps()
