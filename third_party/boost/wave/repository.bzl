load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def boost_wave():
    # Version from September 2026 on develop branch - https://github.com/boostorg/wave/tree/7ed288aed82d861afc729b866a07b2c3625cef71
    # Strictly speaking this does not match the boost version we depend on.
    # However, the boost::wave code is backwards compatible to the boost version we use.
    # We want to depend on an old boost to not force an update for clients# using boost as well in their project.
    # Also, using an up to date version of boost::wave is important to get the latest bug fixes.
    git_ref = "7ed288aed82d861afc729b866a07b2c3625cef71"
    maybe(
        http_archive,
        name = "boost.wave",
        sha256 = "066b2c384929f1f9578e6eee9f203e5c39805d82cec128ce41f8e55c9896bf93",
        strip_prefix = "wave-" + git_ref,
        urls = ["https://github.com/boostorg/wave/archive/" + git_ref + ".tar.gz"],
        build_file = Label("//third_party/boost/wave:wave.BUILD"),
        patches = [
            # Can be dropped after https://github.com/boostorg/wave/issues/263 is resolved upstream
            Label("//third_party/boost/wave:properly_set_cplusplus.patch"),
        ],
        patch_args = ["-p1"],
    )
