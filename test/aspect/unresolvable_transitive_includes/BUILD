load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "use_impl_dep_after_own_header",
    srcs = ["use_libs.cpp"],
    hdrs = ["use_libs.h"],
    implementation_deps = ["//unresolvable_transitive_includes/support:impl_dep"],
    deps = ["//unresolvable_transitive_includes/support:heavy"],
)
