load("@rules_cc//cc:cc_library.bzl", "cc_library")

cc_library(
    name = "complex_includes",
    srcs = ["complex_includes.cpp"],
    hdrs = [
        "some/dir/complex_include_a.h",
        "some/dir/complex_include_b.h",
    ],
    include_prefix = "virtual/prefix",
    includes = ["some"],
    strip_include_prefix = "some",
    visibility = ["//visibility:public"],
)

cc_library(
    name = "use_complex_includes",
    srcs = ["use_complex_includes.cpp"],
    visibility = ["//visibility:public"],
    deps = [":complex_includes"],
)
