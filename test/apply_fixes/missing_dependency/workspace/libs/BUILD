cc_library(
    name = "foo",
    hdrs = ["foo.h"],
    visibility = ["//visibility:public"],
    deps = ["//other_lib"],
)

cc_library(
    name = "bar",
    hdrs = ["sub/bar.h"],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "manipulated_bar",
    hdrs = ["sub/bar.h"],
    include_prefix = "new/path",
    strip_include_prefix = ".",
    visibility = ["//visibility:public"],
)

# Ensure we can parse attributes which are explicitly set to an empty list. Those are represented differently in a query
# compared to omitting the targets completely.
cc_library(
    name = "empty_lists",
    srcs = [],
    hdrs = [],
    visibility = ["//visibility:public"],
)
