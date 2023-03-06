genrule(
    name = "foo_h",
    outs = ["foo.h"],
    cmd = "echo 'int doGenerated() { return 42; }' > \"$@\"",
)

cc_library(
    name = "foo",
    hdrs = ["foo.h"],
    visibility = ["//visibility:public"],
)
