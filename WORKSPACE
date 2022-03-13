workspace(name = "depend_on_what_you_use")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

#
# External dependencies
#

http_archive(
    name = "rules_python",
    sha256 = "a30abdfc7126d497a7698c29c46ea9901c6392d6ed315171a6df5ce433aa4502",
    strip_prefix = "rules_python-0.6.0",
    urls = ["https://github.com/bazelbuild/rules_python/archive/0.6.0.tar.gz"],
)

http_archive(
    name = "bazel_skylib",
    sha256 = "c6966ec828da198c5d9adbaa94c05e3a1c7f21bd012a0b29ba8ddbccb2c93b0d",
    urls = ["https://github.com/bazelbuild/bazel-skylib/releases/download/1.1.1/bazel-skylib-1.1.1.tar.gz"],
)

load("@bazel_skylib//:workspace.bzl", "bazel_skylib_workspace")

bazel_skylib_workspace()

#
# Project
#

load("@bazel_skylib//lib:versions.bzl", "versions")

versions.check(
    maximum_bazel_version = "6.0.0-pre.20220216.3",
    minimum_bazel_version = "4.0.0",
)

#
# Testing
#

load("//test:test.bzl", "test_setup")

test_setup()
