load("@rules_cc//cc:cc_library.bzl", "cc_library")

# Using the headers from 'transitive_dep' will cause a DWYU failure unless those headers are ignored with a custom config
cc_library(
    name = "direct_dep",
    visibility = ["//ignore_includes:__pkg__"],
    deps = [":transitive_dep"],
)

cc_library(
    name = "transitive_dep",
    hdrs = [
        "a_substring_match_does_not_work_here.h",
        "do_match_include_end.h",
        "ignored_sub_path_1/some_header.h",
        "ignored_sub_path_2/some_header.h",
        "matching_begin_without_regex_works_example.h",
        "some_header.h",
        "some_other_header.h",
    ],
)
