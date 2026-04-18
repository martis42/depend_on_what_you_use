load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "ok_target",
    srcs = ["use_lib.cpp"],
    # Which features are active is not important as long as they are not configured to skip the DWYU analysis.
    features = ["random_feature"],
    deps = ["//skip_features/support:lib"],
)

# Would fail DWYU analysis if it is not being skipped
cc_library(
    name = "skip_target_because_of_active_feature",
    srcs = ["use_lib.cpp"],
    # The default compilation mode is 'fastbuild'. By setting the 'dbg' feature here, we trigger the DWYU skip logic
    # we configured for the test.
    features = ["dbg"],
    deps = ["//skip_features/support:lib_indirection"],
)

# Would fail DWYU analysis if it is not being skipped
cc_library(
    name = "skip_target_because_of_inactive_feature",
    srcs = ["use_lib.cpp"],
    # The default compilation mode is 'fastbuild'. By disabling 'fastbuild' here, we trigger the DWYU skip logic
    # we configured for the test.
    features = ["-fastbuild"],
    deps = ["//skip_features/support:lib_indirection"],
)
