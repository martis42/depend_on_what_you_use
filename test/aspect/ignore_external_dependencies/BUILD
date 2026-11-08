load("@rules_cc//cc:cc_library.bzl", "cc_library")

##
## Test Targets
##

# External usage

cc_library(
    name = "use_external_dep_privately",
    srcs = ["use_external_dep_privately.cpp"],
    deps = ["@ignore_external_dependencies_test_repo//:foo"],
)

cc_library(
    name = "unused_external_deps",
    srcs = ["unused_external_deps.cpp"],
    implementation_deps = ["@ignore_external_dependencies_test_repo//:foo"],
    deps = ["@ignore_external_dependencies_test_repo//:bar"],
)

cc_library(
    name = "use_external_generated_header",
    srcs = ["use_external_generated_header.cpp"],
    deps = [":bridge"],
)

cc_library(
    name = "use_external_tree_header",
    srcs = ["use_external_tree_header.cpp"],
    deps = [":bridge"],
)

cc_library(
    name = "use_external_virtual_header",
    srcs = ["use_external_virtual_header.cpp"],
    deps = [":bridge"],
)

cc_library(
    name = "use_transitive_external_header",
    srcs = ["use_transitive_external_header.cpp"],
    deps = [":bridge"],
)

cc_library(
    name = "use_transitive_external_header_with_ignore_via_tag",
    srcs = ["use_transitive_external_header.cpp"],
    tags = ["dwyu:ignore_external_dependencies=true"],
    deps = [":bridge"],
)

cc_library(
    name = "use_transitive_external_header_fails_due_to_disabling_by_tag",
    srcs = ["use_transitive_external_header.cpp"],
    tags = ["dwyu:ignore_external_dependencies=false"],
    deps = [":bridge"],
)

# Internal usage

cc_library(
    name = "unused_internal_deps",
    srcs = ["unused_internal_deps.cpp"],
    deps = [":local_header"],
)

# We use a header from an internal 'external' directory to prove this does not throw off our heuristic
cc_library(
    name = "use_transitive_internal_header",
    srcs = ["use_transitive_internal_header.cpp"],
    deps = [":bridge"],
)

##
## Support
##

cc_library(
    name = "bridge",
    hdrs = ["bridge.h"],
    deps = [
        ":local_header",  # used
        "@ignore_external_dependencies_test_repo//:foo",  # used
        "@ignore_external_dependencies_test_repo//:generated",  # used
        "@ignore_external_dependencies_test_repo//:tree",  # used
        "@ignore_external_dependencies_test_repo//:virtual",  # used
    ],
)

cc_library(
    name = "local_header",
    hdrs = ["external/local.h"],
)
