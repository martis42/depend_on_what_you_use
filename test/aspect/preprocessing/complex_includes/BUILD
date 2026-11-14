load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "use_system_includes",
    srcs = ["use_system_includes.cpp"],
    deps = [
        ":system_header",
        "//preprocessing/support:lib_a",
    ],
)

cc_library(
    name = "system_header",
    hdrs = ["system/system_header.h"],
    includes = ["system"],
)

cc_library(
    name = "use_virtual_includes",
    srcs = ["use_virtual_includes.cpp"],
    deps = [
        ":virtual_headers",
        "//preprocessing/support:lib_a",
    ],
)

cc_library(
    name = "virtual_headers",
    hdrs = [
        "include/first.h",
        "include/second.h",
    ],
    include_prefix = "complex_virtual",
    strip_include_prefix = "include",
)

cc_library(
    name = "use_external_includes",
    srcs = ["use_external_includes.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "@external_test_repo//:ext_bar",
        "@external_test_repo//:ext_foo",
        "@ignore_external_dependencies_test_repo//:generated",
        "@ignore_external_dependencies_test_repo//:tree",
        "@ignore_external_dependencies_test_repo//:virtual",
    ],
)

cc_library(
    name = "use_external_complex_includes",
    srcs = ["use_external_complex_includes.cpp"],
    deps = [
        "//preprocessing/support:lib_a",
        "@complex_includes_test_repo//:complex_includes",
    ],
)
