load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")
load("@rules_cc//cc:cc_test.bzl", "cc_test")

cc_library(
    name = "foo",
    hdrs = ["foo.h"],
)

cc_library(
    name = "bar",
    hdrs = ["bar.h"],
)

cc_library(
    name = "proper_private_deps",
    srcs = ["use_libs.cpp"],
    hdrs = ["use_libs.h"],
    implementation_deps = [":foo"],
    deps = [":bar"],
)

cc_library(
    name = "superfluous_public_dep",
    srcs = ["use_libs.cpp"],
    hdrs = ["use_libs.h"],
    deps = [
        ":bar",
        ":foo",
    ],
)

cc_library(
    name = "use_complex_includes",
    srcs = ["use_complex_includes.cpp"],
    hdrs = ["use_complex_includes.h"],
    implementation_deps = [
        "//implementation_deps/support:lib_with_add_prefix",
        "//implementation_deps/support:lib_with_includes",
        "//implementation_deps/support:lib_with_strip_prefix",
    ],
)

cc_library(
    name = "use_defines",
    srcs = ["use_defines.cpp"],
    hdrs = ["use_defines.h"],
    implementation_deps = [
        "//implementation_deps/support:lib_with_defines",
    ],
)

cc_library(
    name = "use_external",
    srcs = ["use_external.cpp"],
    hdrs = ["use_external.h"],
    implementation_deps = [
        "@impl_deps_external_test_repo//:ext_lib",
        "@impl_deps_external_test_repo//:lib_with_add_prefix",
        "@impl_deps_external_test_repo//:lib_with_includes",
        "@impl_deps_external_test_repo//:lib_with_strip_prefix",
    ],
)

cc_binary(
    name = "binary_using_foo",
    srcs = ["binary_using_foo.cpp"],
    deps = [":foo"],
)

cc_test(
    name = "test_using_foo",
    srcs = ["binary_using_foo.cpp"],
    deps = [":foo"],
)
