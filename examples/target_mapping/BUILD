load("@rules_cc//cc:cc_binary.bzl", "cc_binary")

cc_binary(
    name = "use_lib_b",
    srcs = ["use_lib_b.cpp"],
    deps = ["//target_mapping/libs:a"],
)

cc_binary(
    name = "use_lib_c",
    srcs = ["use_lib_c.cpp"],
    deps = ["//target_mapping/libs:a"],
)
