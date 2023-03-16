##############
# Test Cases #
##############

cc_binary(
    name = "use_libs",
    srcs = ["use_libs.cpp"],
    deps = [":libs_provider"],
)

cc_binary(
    name = "use_ambiguous_lib",
    srcs = ["use_ambiguous_lib.cpp"],
    deps = [":ambiguous_lib_provider"],
)

cc_binary(
    name = "use_private_header",
    srcs = ["use_private_header.cpp"],
    deps = [":use_private_header_provider"],
)

cc_binary(
    name = "use_generated_code",
    srcs = ["use_generated_code.cpp"],
    deps = [":generated_code_provider"],
)

cc_binary(
    name = "use_external_dep",
    srcs = ["use_external_dep.cpp"],
    deps = [":external_dep_provider"],
)

cc_library(
    name = "use_libs_privately",
    srcs = ["use_libs.cpp"],
    implementation_deps = [":libs_provider"],
)

cc_library(
    name = "mixed_libs_usage",
    srcs = ["mixed_libs_usage.cpp"],
    hdrs = ["mixed_libs_usage.h"],
    deps = [":libs_provider"],
)

##################
# Helper Targets #
##################

cc_library(
    name = "ambiguous_lib_provider",
    srcs = ["dummy.h"],
    deps = [
        "//ambiguous_lib:lib_a",
        "//ambiguous_lib:lib_b",
    ],
)

cc_library(
    name = "libs_provider",
    srcs = ["dummy.h"],
    deps = [
        ":root_file_lib",
        "//libs:bar",
        "//libs:foo",
    ],
)

cc_library(
    name = "use_private_header_provider",
    srcs = ["dummy.h"],
    deps = ["//private_header"],
)

cc_library(
    name = "generated_code_provider",
    srcs = ["dummy.h"],
    deps = ["//generate_code:foo"],
)

cc_library(
    name = "external_dep_provider",
    srcs = ["dummy.h"],
    deps = [
        "@external_dep//:foo",
        "@external_dep//sub/dir:bar",
    ],
)

cc_library(
    name = "root_file_lib",
    hdrs = ["root_lib.h"],
)
