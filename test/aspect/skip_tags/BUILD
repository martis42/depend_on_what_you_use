load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "unused_lib",
    hdrs = ["foo.h"],
)

# Inspection this with the default configuration should not fail
cc_library(
    name = "ignored_by_default_behavior",
    hdrs = ["bar.h"],
    tags = ["no-dwyu"],
    deps = [":unused_lib"],
)

# Inspection this should not fail with aspect configured to skip 'tag_marking_skipping' tags
cc_library(
    name = "ignored_by_custom_tag",
    hdrs = ["bar.h"],
    tags = [
        "some_tag",
        "tag_marking_skipping",
    ],
    deps = [":unused_lib"],
)
