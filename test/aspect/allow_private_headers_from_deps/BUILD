load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "use_private_headers_from_deps",
    srcs = ["use_private_headers_from_deps.cpp"],
    hdrs = ["use_private_headers_from_deps.h"],
    implementation_deps = [":dep_b"],
    deps = [":dep_a"],
)

cc_library(
    name = "allow_private_headers_from_deps_via_tag",
    srcs = ["use_private_headers_from_deps.cpp"],
    hdrs = ["use_private_headers_from_deps.h"],
    implementation_deps = [":dep_b"],
    tags = ["dwyu:ignore_private_headers_from_deps=False"],
    deps = [":dep_a"],
)

cc_library(
    name = "forbid_private_headers_from_deps_via_tag",
    srcs = ["use_private_headers_from_deps.cpp"],
    hdrs = ["use_private_headers_from_deps.h"],
    implementation_deps = [":dep_b"],
    tags = ["dwyu:ignore_private_headers_from_deps=True"],
    deps = [":dep_a"],
)

cc_library(
    name = "dep_a",
    srcs = ["private_a.h"],
)

cc_library(
    name = "dep_b",
    srcs = ["private_b.h"],
)
