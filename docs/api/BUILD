load(":stardoc_with_diff_test.bzl", "stardoc", "update_and_test_docs")

stardoc(
    name = "cc_info_mapping",
    bzl_target = "//dwyu/cc_info_mapping:cc_info_mapping_bzl",
    out_file = "cc_info_mapping.md",
)

stardoc(
    name = "dwyu_aspect",
    bzl_target = "//dwyu/aspect:factory_bzl",
    out_file = "dwyu_aspect.md",
)

update_and_test_docs()
