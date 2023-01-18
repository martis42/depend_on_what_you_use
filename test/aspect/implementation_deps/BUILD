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
