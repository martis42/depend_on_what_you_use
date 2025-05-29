load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "bad_target",
    hdrs = ["use_transitive_dep.h"],
    deps = [":lib_a"],
)

cc_library(
    name = "bad_target_skipped",
    hdrs = ["use_transitive_dep.h"],
    tags = ["no-dwyu"],
    deps = [":lib_a"],
)

cc_library(
    name = "bad_target_custom_skip",
    hdrs = ["use_transitive_dep.h"],
    tags = ["my_tag"],
    deps = [":lib_a"],
)

cc_library(
    name = "lib_a",
    hdrs = ["lib_a.h"],
    deps = [":lib_b"],
)

cc_library(
    name = "lib_b",
    hdrs = ["lib_b.h"],
)

cc_library(
    name = "use_broken_external_dependency",
    hdrs = ["use_broken_external_dependency.h"],
    deps = ["@external_targets//:has_unused_dep"],
)
