load("@bazel_skylib//lib:unittest.bzl", "analysistest", "asserts")
load("//dwyu/cc/cc_info_mapping:providers.bzl", "DwyuRemappedCcInfo")

def _direct_deps_are_included_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    direct_headers = [h.basename for h in headers]

    expected_headers = ["lib_with_dep.h", "dep_layer_1.h"]
    asserts.equals(env, expected_headers, direct_headers)

    return analysistest.end(env)

direct_deps_are_included_test = analysistest.make(_direct_deps_are_included_test_impl)

def _implementation_deps_are_excluded_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    direct_headers = [h.basename for h in headers]

    expected_headers = ["lib_with_impl_dep.h"]
    asserts.equals(env, expected_headers, direct_headers)

    return analysistest.end(env)

implementation_deps_are_excluded_test = analysistest.make(_implementation_deps_are_excluded_test_impl)

def _non_cc_dep_is_skipped_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    direct_headers = [h.basename for h in headers]

    expected_headers = ["lib_with_non_cc_dep.h"]
    asserts.equals(env, expected_headers, direct_headers)

    return analysistest.end(env)

non_cc_dep_is_skipped_test = analysistest.make(_non_cc_dep_is_skipped_test_impl)

def _custom_non_cc_deps_are_skipped_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = [h.basename for h in headers]

    asserts.equals(env, ["custom_cc_info_with_non_cc_deps.h", "dep_layer_1.h"], header_names)

    return analysistest.end(env)

custom_non_cc_deps_are_skipped_test = analysistest.make(_custom_non_cc_deps_are_skipped_test_impl)

def _filter_selects_only_matching_dep_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    direct_headers = [h.basename for h in headers]

    expected_headers = ["lib_with_two_deps.h", "dep_layer_1.h"]
    asserts.equals(env, expected_headers, direct_headers)

    return analysistest.end(env)

filter_selects_only_matching_dep_test = analysistest.make(_filter_selects_only_matching_dep_test_impl)

def direct_deps_test_suite(name):
    direct_deps_are_included_test(
        name = "mapping_to_direct_deps_finds_headers",
        target_under_test = ":mapping_to_direct_deps",
    )
    implementation_deps_are_excluded_test(
        name = "mapping_to_direct_deps_skips_impl_deps",
        target_under_test = ":mapping_to_direct_deps_with_impl_dep",
    )
    non_cc_dep_is_skipped_test(
        name = "mapping_to_direct_deps_skips_non_cc_deps",
        target_under_test = ":mapping_to_direct_deps_with_non_cc_dep",
    )
    custom_non_cc_deps_are_skipped_test(
        name = "mapping_to_direct_deps_skips_custom_non_cc_deps",
        target_under_test = ":mapping_to_direct_deps_with_custom_non_cc_deps",
    )
    filter_selects_only_matching_dep_test(
        name = "mapping_to_direct_deps_filter_selects_only_matching_dep",
        target_under_test = ":mapping_to_direct_deps_with_filter",
    )
    native.test_suite(
        name = name,
        tests = [
            ":mapping_to_direct_deps_finds_headers",
            ":mapping_to_direct_deps_skips_impl_deps",
            ":mapping_to_direct_deps_skips_non_cc_deps",
            ":mapping_to_direct_deps_skips_custom_non_cc_deps",
            ":mapping_to_direct_deps_filter_selects_only_matching_dep",
        ],
    )
