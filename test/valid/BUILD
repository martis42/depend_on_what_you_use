cc_library(
    name = "foo",
    hdrs = [
        "foo/a.h",
        "foo/b.h",
    ],
    textual_hdrs = ["foo/textual.cc"],
)

cc_library(
    name = "bar",
    srcs = [
        "bar/bar.cc",
        "bar/private_a.h",
        "bar/sub/dir/private_b.h",
    ],
    hdrs = ["bar/bar.h"],
    deps = [":foo"],
)
