load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def rules_boost_step_1():
    """
    For more, see https://github.com/nelhage/rules_boost and https://www.boost.org

    It is cumbersome to depend on boost like this. Also, those rules are no longer actively maintained.
    However, we are not yet ready to abandon the WORKSPACE support and thus for now have to use this legacy solution.
    """
    maybe(
        http_archive,
        name = "com_github_nelhage_rules_boost",
        sha256 = "4ebeaa6c71c11034efc9e1b85cc20a899a3ed54dc8e03c38ebd3caed362f652c",
        strip_prefix = "rules_boost-9d42ebfa8ae231a5794040cc06926f467232ee43",
        urls = ["https://github.com/nelhage/rules_boost/archive/9d42ebfa8ae231a5794040cc06926f467232ee43.tar.gz"],
    )
