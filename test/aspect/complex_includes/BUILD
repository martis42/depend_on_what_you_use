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
)

cc_library(
    name = "use_complex_includes",
    srcs = ["use_complex_includes.cpp"],
    deps = [":complex_includes"],
)

cc_library(
    name = "use_complex_includes_from_extern",
    srcs = ["use_complex_includes.cpp"],
    deps = ["@complex_includes_repo//:complex_includes"],
)
