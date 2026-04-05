load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "use_transitive_headers",
    srcs = ["use_transitive_headers.cpp"],
    deps = ["//ignoring_includes/support:foo"],
)

exports_files(["ignore_includes.json"])
