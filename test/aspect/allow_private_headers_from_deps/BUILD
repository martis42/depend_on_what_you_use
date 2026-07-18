load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "use_private_headers_from_deps",
    srcs = ["use_private_headers_from_deps.cpp"],
    hdrs = ["use_private_headers_from_deps.h"],
    implementation_deps = [":dep_b"],
    deps = [":dep_a"],
)

cc_library(
    name = "dep_a",
    srcs = ["private_a.h"],
    # without a public header we cannot trigger the 'unused dependency' error, since dependencies offering no usable headers are pruned early int he analysis
    hdrs = ["dep.h"],
)

cc_library(
    name = "dep_b",
    srcs = ["private_b.h"],
    # without a public header we cannot trigger the 'unused dependency' error, since dependencies offering no usable headers are pruned early int he analysis
    hdrs = ["dep.h"],
)
