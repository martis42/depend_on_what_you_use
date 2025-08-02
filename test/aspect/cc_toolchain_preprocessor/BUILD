load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "use_extern_valid",
    srcs = ["use_extern_valid.cpp"],
    deps = [
        "@external_includes_test_repo//:ext_lib",
        "@external_includes_test_repo//foo:lib",
    ],
)

cc_library(
    name = "use_extern_invalid",
    srcs = ["use_extern_invalid.cpp"],
    deps = [
        # Depend on ext_lib, but use transitive foo/lib.h in code
        "@external_includes_test_repo//:ext_lib",
    ],
)
