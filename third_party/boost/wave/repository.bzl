load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def boost_wave():
    # Version from April 2026 - https://github.com/boostorg/wave/tree/44b4b6064f875f9a121a109a4d60c60ba74062f4
    # Strictly speaking this does not match the boost version we depend on. However, the boost::wave code is backwards
    # compatible to the boost version we use. We want to depend on an old boost to not force an update for clients
    # using boost as well in their project. Also, using an up to date version of boost::wave is important to get the
    # latest bug fixes.
    git_ref = "44b4b6064f875f9a121a109a4d60c60ba74062f4"
    maybe(
        http_archive,
        name = "boost.wave",
        sha256 = "32344960683b0c1e7705d48fec88a2c6a22143d1e7619649fadd057e8eeac0c3",
        strip_prefix = "wave-" + git_ref,
        urls = ["https://github.com/boostorg/wave/archive/" + git_ref + ".tar.gz"],
        build_file = Label("//third_party/boost/wave:wave.BUILD"),
        patches = [
            # Bazel sets the macros __DATE__ and __TIME__ to the constant value 'redacted' to make sure the output of
            # CC actions is as static as possible to ensure caching of build actions works properly. This constant
            # value is however breaking some internal logic in boost::wave, which consumes those macros.
            # As far as we can tell, nothing of relevance with respect to our use cases is done in boost::wave with
            # that information. Thus, we simply disable the failing logic in boost::wave by commenting it out.
            Label("//third_party/boost/wave:ignore_time_and_version.patch"),
            # boost::wave is setting some macros based on internal logic and does not allow overwriting them
            # (e.g. __cplusplus). However, we want full control over all macros. Thus, we introduce a flag allowing
            # us to overwrite all macros on demand.
            Label("//third_party/boost/wave:allow_overwriting_all_macros.patch"),
        ],
    )
