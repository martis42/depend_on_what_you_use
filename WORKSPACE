workspace(name = "depend_on_what_you_use")

#
# Dependencies
#

load("//:dependencies.bzl", "private_dependencies", "public_dependencies")

public_dependencies()

private_dependencies()

load("@bazel_skylib//:workspace.bzl", "bazel_skylib_workspace")

bazel_skylib_workspace()

#
# Project
#

load("@bazel_skylib//lib:versions.bzl", "versions")

versions.check(
    minimum_bazel_version = "4.0.0",
)

#
# Testing
#

load("//test:test.bzl", "test_setup")

test_setup()
