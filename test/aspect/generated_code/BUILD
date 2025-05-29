load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

genrule(
    name = "bar_h",
    outs = ["bar.h"],
    cmd = "echo '// Header content' > \"$@\"",
)

cc_library(
    name = "bar",
    hdrs = ["bar.h"],
)

cc_binary(
    name = "foo",
    srcs = ["foo.cpp"],
    deps = [":bar"],
)
