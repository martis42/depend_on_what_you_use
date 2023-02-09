workspace(name = "depend_on_what_you_use")

#
# Dependencies
#

load("//:dependencies.bzl", "private_dependencies", "public_dependencies")

public_dependencies()

load("//:extra_deps.bzl", "dwyu_extra_deps")

dwyu_extra_deps()

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

load("@rules_python//python/pip_install:repositories.bzl", "pip_install_dependencies")

pip_install_dependencies()

# This repository isn't referenced, except by our test that asserts the requirements.bzl is updated.
# It also wouldn't be needed by users of this ruleset.
# Ref: https://github.com/bazelbuild/rules_python/blob/main/examples/pip_parse_vendored
load("@rules_python//python:pip.bzl", "pip_parse")

pip_parse(
   name = "dwyu_py_deps",
   requirements_lock = "//third_party:requirements.txt",
)

#
# Testing
#

load("//test/aspect:test.bzl", "test_setup")

test_setup()
