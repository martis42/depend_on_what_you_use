load("@rules_cc//cc:cc_library.bzl", "cc_library")

package(features = ["custom_active_package_feature"])

# Would fail DWYU analysis if it is not being skipped
cc_library(
    name = "skip_target_because_of_package_feature",
    srcs = ["use_lib.cpp"],
    deps = ["//skip_features/support:lib_indirection"],
)

# Would fail DWYU analysis if it is not being skipped
cc_library(
    name = "skip_target_because_of_active_feature",
    srcs = ["use_lib.cpp"],
    features = ["custom_active_feature"],
    deps = ["//skip_features/support:lib_indirection"],
)

# Would fail DWYU analysis if it is not being skipped
cc_library(
    name = "skip_target_because_of_inactive_feature",
    srcs = ["use_lib.cpp"],
    features = ["-custom_inactive_feature"],
    deps = ["//skip_features/support:lib_indirection"],
)
