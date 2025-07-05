load("@aspect_bazel_lib//lib:docs.bzl", "stardoc_with_diff_test", "update_docs")

stardoc_with_diff_test(
    name = "cc_info_mapping",
    bzl_library_target = "//src/cc_info_mapping:cc_info_mapping",
)

stardoc_with_diff_test(
    name = "dwyu_aspect",
    bzl_library_target = "//src/aspect:factory",
)

stardoc_with_diff_test(
    name = "toolchain_headers",
    bzl_library_target = "//src/toolchain_headers:toolchain_headers",
)

update_docs()
