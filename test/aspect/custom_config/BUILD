exports_files([
    "extra_ignore_include_paths.json",
    "full_custom_config.json",
    "ignore_include_paths.json",
    "ignore_include_patterns.json",
])

# Has an invalid include besides a standard include, which does however not cause an error due to the ignore list in the config
cc_library(
    name = "use_arcane_header_and_vector",
    hdrs = ["use_arcane_header_and_vector.h"],
)

# Has an invalid include, which does however not cause an error due to the ignore list in the config
cc_library(
    name = "use_arcane_header",
    hdrs = ["use_arcane_header.h"],
)

# Has multiple invalid includes, which do however not cause an error due to the ignore lists in the config
cc_library(
    name = "use_multiple_arcane_headers",
    hdrs = ["use_multiple_arcane_headers.h"],
)

# Has multiple invalid includes, which do however not cause an error due to them matching the ignored patterns
cc_library(
    name = "use_ignored_patterns",
    hdrs = ["use_ignored_patterns.h"],
)
