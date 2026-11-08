load("@rules_cc//cc:cc_library.bzl", "cc_library")
load(":tree.bzl", "external_header_tree")

exports_files(
    ["foo.h"],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "foo",
    hdrs = ["foo.h"],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "bar",
    hdrs = ["bar.h"],
    visibility = ["//visibility:public"],
)

cc_library(
    name = "virtual",
    hdrs = ["some/dir/complex_include_a.h"],
    include_prefix = "virtual/prefix",
    strip_include_prefix = "some",
    visibility = ["//visibility:public"],
)

genrule(
    name = "generate_header",
    # We have to generate a directory with a file extensions accepted by cc_library.hdrs to be able to wrap the result in a cc_library
    outs = ["generated_external.h"],
    cmd = "printf '%s\\n' '#ifndef GENERATED_EXTERNAL_H' '#define GENERATED_EXTERNAL_H' 'int generatedExternal();' '#endif' > $@",
)

cc_library(
    name = "generated",
    hdrs = [":generated_external.h"],
    visibility = ["//visibility:public"],
)

external_header_tree(name = "generated_tree.h")

cc_library(
    name = "tree",
    hdrs = [":generated_tree.h"],
    visibility = ["//visibility:public"],
)
