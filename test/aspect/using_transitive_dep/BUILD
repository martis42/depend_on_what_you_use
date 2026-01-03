load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    deps = [":direct_dep"],
)

cc_library(
    name = "transitive_usage_through_impl_deps",
    srcs = ["transitive_usage_through_impl_deps.h"],
    implementation_deps = [":direct_dep"],
)

##
## Support
##

cc_library(
    name = "direct_dep",
    hdrs = ["direct_dep.h"],
    deps = [":transitive_dep"],
)

cc_library(
    name = "transitive_dep",
    srcs = ["transitive_dep_src.h"],
    hdrs = ["transitive_dep_hdr.h"],
)
