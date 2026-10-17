load("@rules_cc//cc:cc_library.bzl", "cc_library")

package(default_visibility = ["//preprocessing:__subpackages__"])

cc_library(
    name = "lib_exporting_defines_a",
    hdrs = ["lib_exporting_defines_a.h"],
    defines = [
        "DEP_EXPORTED_DEFINE",
    ],
    # Local defines are not supposed to be visible to users of this library
    local_defines = ["DEP_LOCAL_DEFINE"],
    deps = [":lib_exporting_defines_transitively_a"],
)

cc_library(
    name = "lib_exporting_defines_b",
    hdrs = ["lib_exporting_defines_b.h"],
    defines = [
        "DEP_EXPORTED_VALUE=42",
    ],
    # Defines coming from implementation deps are not supposed to be visible to users of this library
    implementation_deps = [":lib_exporting_defines_transitively_b"],
    local_defines = ["DEP_LOCAL_DEFINE"],
)

cc_library(
    name = "lib_exporting_defines_transitively_a",
    defines = ["DEP_TRANSITIVE_DEFINE_A"],
)

cc_library(
    name = "lib_exporting_defines_transitively_b",
    defines = ["DEP_TRANSITIVE_DEFINE_B"],
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
