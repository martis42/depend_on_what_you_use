load("@bazel_skylib//lib:unittest.bzl", "analysistest", "asserts")
load("//dwyu/cc/cc_info_mapping:providers.bzl", "DwyuCcInfoMappingInfo")

def _custom_and_builtin_mappings_test_impl(ctx):
    env = analysistest.begin(ctx)
    mapping = analysistest.target_under_test(env)[DwyuCcInfoMappingInfo].mapping
    labels = sorted([str(label) for label in mapping])
    asserts.equals(env, sorted([
        str(Label("//dwyu/cc/cc_info_mapping/test:lib_with_dep")),
        str(Label("//dwyu/cc/cc_info_mapping/test:other_lib")),
    ]), labels)
    asserts.equals(
        env,
        ["dep.h", "lib_with_dep.h"],
        sorted([header.basename for header in mapping[Label("//dwyu/cc/cc_info_mapping/test:lib_with_dep")].compilation_context.direct_headers]),
    )
    return analysistest.end(env)

custom_and_builtin_mappings_test = analysistest.make(_custom_and_builtin_mappings_test_impl)

def _duplicate_mappings_test_impl(ctx):
    env = analysistest.begin(ctx)
    asserts.expect_failure(env, "DWYU: Multiple remappings for target")
    return analysistest.end(env)

duplicate_mappings_test = analysistest.make(_duplicate_mappings_test_impl, expect_failure = True)

def _invalid_target_test_impl(ctx):
    env = analysistest.begin(ctx)
    asserts.expect_failure(env, "must provide a Label as target")
    return analysistest.end(env)

invalid_target_test = analysistest.make(_invalid_target_test_impl, expect_failure = True)

def _invalid_cc_info_test_impl(ctx):
    env = analysistest.begin(ctx)
    asserts.expect_failure(env, "must provide a CcInfo as cc_info")
    return analysistest.end(env)

invalid_cc_info_test = analysistest.make(_invalid_cc_info_test_impl, expect_failure = True)

def aggregation_test_suite(name):
    custom_and_builtin_mappings_test(
        name = "custom_and_builtin_mappings_are_aggregated",
        target_under_test = ":mapping_with_custom_and_builtin",
    )
    duplicate_mappings_test(
        name = "custom_and_builtin_duplicate_mappings_fail",
        target_under_test = ":mapping_with_custom_and_builtin_duplicate",
    )
    duplicate_mappings_test(
        name = "duplicate_custom_mappings_fail",
        target_under_test = ":mapping_with_custom_duplicate",
    )
    invalid_target_test(
        name = "invalid_remapping_target_fails",
        target_under_test = ":mapping_with_invalid_target",
    )
    invalid_cc_info_test(
        name = "invalid_remapping_cc_info_fails",
        target_under_test = ":mapping_with_invalid_cc_info",
    )
    native.test_suite(
        name = name,
        tests = [
            ":custom_and_builtin_mappings_are_aggregated",
            ":custom_and_builtin_duplicate_mappings_fail",
            ":duplicate_custom_mappings_fail",
            ":invalid_remapping_target_fails",
            ":invalid_remapping_cc_info_fails",
        ],
    )
