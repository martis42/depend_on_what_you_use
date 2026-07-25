load("@rules_cc//cc:cc_library.bzl", "cc_library")
load(":to_canonical.bzl", "to_canonical")

cc_library(
    name = "foo",
    hdrs = ["foo.h"],
)

cc_library(
    name = "lib_with_unused_deps",
    srcs = ["lib.cpp"],
    hdrs = ["lib.h"],
    implementation_deps = ["@ignore_unused_deps_test_repo//:ext"],
    deps = [":foo"],
)

cc_library(
    name = "lib_with_unused_deps_ignored_by_tag",
    srcs = ["lib.cpp"],
    hdrs = ["lib.h"],
    implementation_deps = ["@ignore_unused_deps_test_repo//:ext"],
    tags = [
        "dwyu:ignore_unused_dep={}".format(to_canonical("//ignore_unused_deps:foo")),
        "dwyu:ignore_unused_dep={}".format(to_canonical("@ignore_unused_deps_test_repo//:ext")),
    ],
    deps = [":foo"],
)
