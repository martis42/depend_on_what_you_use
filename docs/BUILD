load("@aspect_bazel_lib//lib:docs.bzl", "stardoc_with_diff_test", "update_docs")

stardoc_with_diff_test(
    name = "cc_info_mapping",
    bzl_library_target = "//dwyu/cc_info_mapping:cc_info_mapping",
)

stardoc_with_diff_test(
    name = "dwyu_aspect",
    bzl_library_target = "//dwyu/aspect:factory",
)

update_docs()
