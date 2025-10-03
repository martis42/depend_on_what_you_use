load("@rules_cc//cc:cc_library.bzl", "cc_library")

exports_files([
    "extra_ignore_include_paths.json",
    "ignore_include_paths.json",
    "ignore_include_patterns.json",
])

# TODO Fix regarding toolchain headers
# Has an invalid include besides a standard include, which does however not cause an error due to the ignore list in the config
cc_library(
    name = "use_ignored_header_and_std_lib",
    hdrs = ["use_ignored_header_and_std_lib.h"],
    deps = ["//ignore_includes/support:direct_dep"],
)

# Has multiple invalid includes, which do however not cause an error due to the ignore lists in the config
cc_library(
    name = "use_multiple_ignored_headers",
    hdrs = ["use_multiple_ignored_headers.h"],
    deps = ["//ignore_includes/support:direct_dep"],
)

# Has multiple invalid includes, which do however not cause an error due to them matching the ignored patterns
cc_library(
    name = "use_ignored_patterns",
    hdrs = ["use_ignored_patterns.h"],
    deps = ["//ignore_includes/support:direct_dep"],
)

# Has an invalid include which is not filtered out by the ignored patterns
cc_library(
    name = "use_not_ignored_header",
    hdrs = ["use_not_ignored_header.h"],
    deps = ["//ignore_includes/support:direct_dep"],
)
