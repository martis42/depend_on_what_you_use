load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def rules_boost():
    # Keep in sync with MODULE.bazel
    maybe(
        http_archive,
        name = "com_github_nelhage_rules_boost",
        sha256 = "d62605b3554f9cc3d6e6bfafdb9d966ebada32c32cfefacba317869dbc97d621",
        urls = ["https://github.com/nelhage/rules_boost/archive/2a7a2ad203e469276540cb7d260e8bd46f6cc030.tar.gz"],
        strip_prefix = "rules_boost-2a7a2ad203e469276540cb7d260e8bd46f6cc030",
    )
