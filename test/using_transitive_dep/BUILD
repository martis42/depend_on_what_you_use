cc_library(
    name = "foo",
    hdrs = ["foo.h"],
)

cc_library(
    name = "bar",
    hdrs = ["bar.h"],
    deps = [":foo"],
)

cc_binary(
    name = "main",
    srcs = ["main.cpp"],
    deps = [":bar"],
)
