load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "foo",
    hdrs = ["foo.h"],
)

cc_library(
    name = "bar",
    hdrs = ["bar.h"],
)

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    deps = [
        ":bar",
        ":foo",  # unused dependency
    ],
)

cc_binary(
    name = "unused_deps_allowed_by_tag",
    srcs = ["main.cpp"],
    tags = ["dwyu:report_unused_deps=False"],
    deps = [
        ":bar",
        ":foo",  # unused dependency
    ],
)

cc_binary(
    name = "unused_deps_disallowed_by_tag",
    srcs = ["main.cpp"],
    tags = ["dwyu:report_unused_deps=True"],
    deps = [
        ":bar",
        ":foo",  # unused dependency
    ],
)

cc_library(
    name = "implementation_deps_lib",
    srcs = ["main.cpp"],
    implementation_deps = [
        ":bar",
        ":foo",  # unused dependency
    ],
)

cc_library(
    name = "unused_deps",
    hdrs = ["unused_deps.h"],
    implementation_deps = [":bar"],
    deps = [":foo"],
)
