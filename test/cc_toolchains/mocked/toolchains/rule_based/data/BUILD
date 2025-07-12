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
    visibility = ["//args:__pkg__"],
)

subdirectory(
    name = "fizz_buzz",
    parent = ":root",
    path = "fizz/buzz",
    visibility = ["//args:__pkg__"],
)

subdirectory(
    name = "foobar",
    parent = ":root",
    path = "foobar",
    visibility = ["//args:__pkg__"],
)
