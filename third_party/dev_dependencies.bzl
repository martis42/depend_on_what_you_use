load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def dev_dependencies():
    version = "4aa11dfdd1958255e133f0d172794d68a0a07b53"
    maybe(
        http_archive,
        name = "mypy_integration",
        sha256 = "24b717883aec8b2234a8f2780e7ea5ddcd5ebbf59acc2f20ff02b31ac7ad7085",
        strip_prefix = "bazel-mypy-integration-{v}".format(v = version),
        urls = ["https://github.com/martis42/bazel-mypy-integration/archive/{v}.tar.gz".format(v = version)],
    )
