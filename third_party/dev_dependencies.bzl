load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def dev_dependencies():
    version = "0a881be043e8eae72ad83610c6205e7972bcd5e1"
    maybe(
        http_archive,
        name = "mypy_integration",
        sha256 = "1b6c3b1d967ae87b83b7ec179a376a4ff501925488bb06960545e776a873aebd",
        strip_prefix = "bazel-mypy-integration-{v}".format(v = version),
        urls = ["https://github.com/martis42/bazel-mypy-integration/archive/{v}.tar.gz".format(v = version)],
    )
