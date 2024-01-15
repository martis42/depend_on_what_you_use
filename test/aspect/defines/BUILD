cc_library(
    name = "in_file_defines",
    hdrs = ["in_file_defines.h"],
    deps = ["//defines/support:lib_a"],
)

cc_library(
    name = "defines_from_bazel_target",
    hdrs = ["defines_from_bazel_target.h"],
    #copts = ["-DSOME_COPT 42"],
    copts = select({
        "@platforms//os:windows": ["/DSOME_COPT 42"],
        "//conditions:default": ["-DSOME_COPT 42"],
    }),
    defines = ["SOME_DEFINE"],
    local_defines = ["LOCAL_DEFINE"],
    deps = ["//defines/support:lib_a"],
)

cc_library(
    name = "transitive_defines_from_bazel_target",
    hdrs = ["transitive_defines_from_bazel_target.h"],
    deps = [
        "//defines/support:lib_a",
        "//defines/support:transitive_define",
    ],
)

cc_library(
    name = "use_defines_from_dependency_header",
    hdrs = ["use_defines_from_dependency_header.h"],
    deps = [
        "//defines/support:conditional_defines",
        "//defines/support:lib_b",
    ],
)

cc_library(
    name = "include_using_pre_processor_token",
    hdrs = ["include_using_pre_processor_token.h"],
    copts = ['-DCONDITIONAL_DEFINES_HEADER=\"defines/support/conditional_defines.h\"'],
    deps = [
        "//defines/support:conditional_defines",
        "//defines/support:lib_a",
        "//defines/support:lib_b",
        "//defines/support:some_defines",
    ],
)
