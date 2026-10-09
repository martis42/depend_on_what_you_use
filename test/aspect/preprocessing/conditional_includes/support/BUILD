load("@rules_cc//cc:cc_library.bzl", "cc_library")

package(default_visibility = ["//preprocessing:__subpackages__"])

cc_library(
    name = "lib_exporting_defines",
    hdrs = ["lib_exporting_defines.h"],
    defines = [
        "DEP_EXPORTED_DEFINE",
        "DEP_EXPORTED_VALUE=42",
    ],
    local_defines = ["DEP_LOCAL_DEFINE"],
    deps = [":lib_exporting_defines_transitively"],
)

cc_library(
    name = "lib_exporting_defines_transitively",
    defines = ["DEP_TRANSITIVE_DEFINE"],
)

cc_library(
    name = "lib_with_macros",
    hdrs = [
        "lib_with_macros.h",
        "lib_with_macros_nested.h",
    ],
)

cc_library(
    name = "lib_include_next_first",
    hdrs = ["include_next/first/next_header.h"],
    includes = ["include_next/first"],
    deps = [":lib_include_next_second"],
)

cc_library(
    name = "lib_include_next_second",
    hdrs = ["include_next/second/next_header.h"],
    includes = ["include_next/second"],
)

cc_library(
    name = "lib_with_include_level",
    hdrs = ["include_level.h"],
)

cc_library(
    name = "lib_with_include_guards",
    hdrs = [
        "guarded_toggle.h",
        "pragma_once_toggle.h",
        "unguarded_toggle.h",
        "variant_macros.h",
    ],
)
