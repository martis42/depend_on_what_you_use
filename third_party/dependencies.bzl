load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")

def dependencies():
    rules_python_version = "0.18.1"
    maybe(
        http_archive,
        name = "rules_python",
        sha256 = "29a801171f7ca190c543406f9894abf2d483c206e14d6acbd695623662320097",
        strip_prefix = "rules_python-{}".format(rules_python_version),
        urls = ["https://github.com/bazelbuild/rules_python/archive/{}.tar.gz".format(rules_python_version)],
    )

    skylib_version = "1.4.1"
    http_archive(
        name = "bazel_skylib",
        sha256 = "b8a1527901774180afc798aeb28c4634bdccf19c4d98e7bdd1ce79d1fe9aaad7",
        urls = ["https://github.com/bazelbuild/bazel-skylib/releases/download/{v}/bazel-skylib-{v}.tar.gz".format(v = skylib_version)],
    )
