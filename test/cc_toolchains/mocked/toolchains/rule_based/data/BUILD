load("@bazel_skylib//rules/directory:directory.bzl", "directory")
load("@bazel_skylib//rules/directory:subdirectory.bzl", "subdirectory")

directory(
    name = "root",
    srcs = glob(["**"]),
)

subdirectory(
    name = "fizz",
    parent = ":root",
    path = "fizz",
    visibility = ["//:__subpackages__"],
)

subdirectory(
    name = "fizz_buzz",
    parent = ":root",
    path = "fizz/buzz",
    visibility = ["//:__subpackages__"],
)

subdirectory(
    name = "foobar",
    parent = ":root",
    path = "foobar",
    visibility = ["//:__subpackages__"],
)
