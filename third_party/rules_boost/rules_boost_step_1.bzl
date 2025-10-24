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
        sha256 = "345c35bdddf386f7a602ae9b9ad194853f25e242cf6f9dbc9187beda6226055c",
        strip_prefix = "rules_boost-84d6dbe4c5feb6f8a9191548190ee80ce902aef7",
        urls = ["https://github.com/nelhage/rules_boost/archive/84d6dbe4c5feb6f8a9191548190ee80ce902aef7.tar.gz"],
    )
