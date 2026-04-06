load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

genrule(
    name = "hdrs",
    outs = [
        "bar.h",
        "baz.h",
    ],
    cmd = """
echo '// bar header' > $(location bar.h)
echo '// baz header' > $(location baz.h)
""",
)

cc_library(
    name = "lib",
    srcs = ["lib.cpp"],
    hdrs = [":hdrs"],
)

cc_binary(
    name = "foo",
    srcs = ["foo.cpp"],
    deps = [":lib"],
)
