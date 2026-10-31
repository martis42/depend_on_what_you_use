load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def boost_wave():
    # Version from October 2026 on develop branch - https://github.com/boostorg/wave/tree/7ed288aed82d861afc729b866a07b2c3625cef71
    # Strictly speaking this does not match the boost version we depend on.
    # However, the boost::wave code is backwards compatible to the boost version we use.
    # We want to depend on an old boost to not force an update for clients using boost as well in their project.
    # Also, using an up to date version of boost::wave is important to get the latest bug fixes.
    git_ref = "38465b8c966b582af128404c4c5e0b798d43c64e"
    maybe(
        http_archive,
        name = "boost.wave",
        sha256 = "32754de914c9bccc565a9d8c34e2535f2c9b9ebf6b0aacb02691cd59ff4fffc2",
        strip_prefix = "wave-" + git_ref,
        urls = ["https://github.com/boostorg/wave/archive/" + git_ref + ".tar.gz"],
        build_file = Label("//third_party/boost/wave:wave.BUILD"),
    )
