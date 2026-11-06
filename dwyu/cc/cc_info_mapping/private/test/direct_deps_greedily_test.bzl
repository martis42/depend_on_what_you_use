load("@bazel_skylib//lib:unittest.bzl", "analysistest", "asserts")
load("//dwyu/cc/cc_info_mapping/private:providers.bzl", "DwyuRemappedCcInfo")

def _all_direct_attributes_are_included_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = sorted([header.basename for header in headers])

    expected_headers = [
        "custom_cc_info_with_nested_custom_deps.h",
        "custom_cc_info_with_unmerged_custom_deps.h",
        "extra_dep.h",
    ]
    asserts.equals(env, expected_headers, header_names)

    return analysistest.end(env)

all_direct_attributes_are_included_test = analysistest.make(_all_direct_attributes_are_included_test_impl)

def _implementation_deps_are_excluded_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = sorted([header.basename for header in headers])

    expected_headers = ["lib_with_impl_dep.h"]
    asserts.equals(env, expected_headers, header_names)

    return analysistest.end(env)

implementation_deps_are_excluded_test = analysistest.make(_implementation_deps_are_excluded_test_impl)

def _filter_selects_only_matching_direct_attribute_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = sorted([header.basename for header in headers])

    expected_headers = ["custom_cc_info_with_unmerged_custom_deps.h", "extra_dep.h"]
    asserts.equals(env, expected_headers, header_names)

    return analysistest.end(env)

filter_selects_only_matching_direct_attribute_test = analysistest.make(_filter_selects_only_matching_direct_attribute_test_impl)

def direct_deps_greedily_test_suite(name):
    all_direct_attributes_are_included_test(
        name = "mapping_to_direct_deps_greedily_includes_direct_attributes_only",
        target_under_test = ":mapping_to_direct_deps_greedily",
    )
    implementation_deps_are_excluded_test(
        name = "mapping_to_direct_deps_greedily_skips_impl_deps",
        target_under_test = ":mapping_to_direct_deps_greedily_with_impl_dep",
    )
    filter_selects_only_matching_direct_attribute_test(
        name = "mapping_to_direct_deps_greedily_filter_selects_only_matching_direct_attribute",
        target_under_test = ":mapping_to_direct_deps_greedily_with_filter",
    )
    native.test_suite(
        name = name,
        tests = [
            ":mapping_to_direct_deps_greedily_includes_direct_attributes_only",
            ":mapping_to_direct_deps_greedily_skips_impl_deps",
            ":mapping_to_direct_deps_greedily_filter_selects_only_matching_direct_attribute",
        ],
    )
