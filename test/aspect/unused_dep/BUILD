cc_library(
    name = "foo",
    hdrs = ["foo.h"],
    visibility = [":__subpackages__"],
)

cc_library(
    name = "bar",
    hdrs = ["bar.h"],
    visibility = [":__subpackages__"],
)

filegroup(
    name = "using_bar",
    srcs = ["main.cpp"],
    visibility = [":__subpackages__"],
)

# ERROR: main uses only bar, but also depends on foo
cc_binary(
    name = "main",
    srcs = [":using_bar"],
    deps = [
        ":bar",
        ":foo",
    ],
)

# SUCCESS: This rule is skipped due to the tag `no-dwyu`.
cc_binary(
    name = "main_skipped",
    srcs = [":using_bar"],
    tags = ["no-dwyu"],
    deps = [
        ":bar",
        ":foo",
    ],
)
