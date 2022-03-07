cc_library(
    name = "foo",
    hdrs = ["foo.h"],
)

cc_library(
    name = "bar",
    hdrs = ["bar.h"],
)

# ERROR: main uses only bar, but also depends on foo
cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    deps = [
        ":bar",
        ":foo",
    ],
)
