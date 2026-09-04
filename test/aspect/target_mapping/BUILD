load("@rules_cc//cc:cc_binary.bzl", "cc_binary")
load("@rules_cc//cc:cc_library.bzl", "cc_library")

# With the correct mapping config the targets do not raise an unused dependency error for //target_mapping/libs:mapped_dep.
# Due to the mapping we believe //target_mapping/libs:mapped_dep offers the headers we include in the test targets

cc_binary(
    name = "use_lib_a_and_ext_a",
    srcs = ["use_lib_a_and_ext_a.cpp"],
    deps = ["//target_mapping/libs:mapped_dep"],
)

cc_library(
    name = "use_lib_a_and_ext_a_privately",
    srcs = ["use_lib_a_and_ext_a.cpp"],
    implementation_deps = ["//target_mapping/libs:mapped_dep"],
)

cc_binary(
    name = "use_lib_b_and_ext_b",
    srcs = ["use_lib_b_and_ext_b.cpp"],
    deps = ["//target_mapping/libs:mapped_dep"],
)
