load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def boost_wave():
    # Version 1.84.0 matches the boost version pulled by rules_boost
    maybe(
        http_archive,
        name = "boost.wave",
        sha256 = "f473a473840519cd5a2497d641733eda195498f46f35716f601e76e69a7a1e3a",
        strip_prefix = "wave-boost-1.84.0",
        urls = ["https://github.com/boostorg/wave/archive/refs/tags/boost-1.84.0.tar.gz"],
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
            Label("//third_party/boost/wave:allow_overwriting_all_maros.patch"),
        ],
    )
