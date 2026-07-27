load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "heavy",
    hdrs = ["heavy.h"],
    visibility = ["//unresolvable_transitive_includes:__pkg__"],
    deps = [":transitive_with_unresolvable_includes"],
)

cc_library(
    name = "impl_dep",
    hdrs = ["impl_dep.h"],
    visibility = ["//unresolvable_transitive_includes:__pkg__"],
)

cc_library(
    name = "transitive_with_unresolvable_includes",
    hdrs = ["transitive_with_unresolvable_includes.h"],
)
