load("@rules_cc//cc:cc_library.bzl", "cc_library")

# Inspecting this fails, unless the target is skipped by a pattern naming it exactly
cc_library(
    name = "broken_exact",
    hdrs = ["bar.h"],
    deps = [":unused_lib"],
)

# This is matched by none of the patterns under test. Thus, inspecting this always fails
cc_library(
    name = "broken_sibling",
    hdrs = ["bar.h"],
    deps = [":unused_lib"],
)

##
## Support Targets
##

cc_library(
    name = "unused_lib",
    hdrs = ["foo.h"],
    visibility = ["//skip_targets:__subpackages__"],
)
