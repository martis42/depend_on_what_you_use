load("@bazel_skylib//lib:unittest.bzl", "analysistest", "asserts")
load("//dwyu/cc/cc_info_mapping/private:providers.bzl", "DwyuRemappedCcInfo")

def _transitive_deps_are_aggregated_greedily_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = sorted([header.basename for header in headers])

    expected_headers = [
        "custom_cc_info_with_custom_deps.h",
        "custom_cc_info_with_nested_custom_deps.h",
        "dep_layer_1.h",
        "dep_layer_2.h",
        "extra_dep.h",
        "lib_with_dep.h",
    ]
    asserts.equals(env, expected_headers, header_names)

    return analysistest.end(env)

transitive_deps_are_aggregated_greedily_test = analysistest.make(_transitive_deps_are_aggregated_greedily_test_impl)

def _greedy_filter_selects_only_matching_direct_dep_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = sorted([header.basename for header in headers])

    expected_headers = ["custom_cc_info_with_custom_deps.h", "extra_dep.h"]
    asserts.equals(env, expected_headers, header_names)

    return analysistest.end(env)

greedy_filter_selects_only_matching_direct_dep_test = analysistest.make(_greedy_filter_selects_only_matching_direct_dep_test_impl)

def _implementation_deps_are_excluded_during_greedy_recursion_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = sorted([header.basename for header in headers])

    expected_headers = [
        "custom_cc_info_with_custom_deps.h",
        "lib_with_impl_dep.h",
    ]
    asserts.equals(env, expected_headers, header_names)

    return analysistest.end(env)

implementation_deps_are_excluded_during_greedy_recursion_test = analysistest.make(_implementation_deps_are_excluded_during_greedy_recursion_test_impl)

def transitive_deps_greedily_test_suite(name):
    transitive_deps_are_aggregated_greedily_test(
        name = "mapping_to_transitive_deps_greedily_aggregates_custom_attrs",
        target_under_test = ":mapping_to_transitive_deps_greedily",
    )
    greedy_filter_selects_only_matching_direct_dep_test(
        name = "mapping_to_transitive_deps_greedily_filter_selects_only_matching_dep",
        target_under_test = ":mapping_to_transitive_deps_greedily_with_filter",
    )
    implementation_deps_are_excluded_during_greedy_recursion_test(
        name = "mapping_to_transitive_deps_greedily_skips_nested_impl_deps",
        target_under_test = ":mapping_to_transitive_deps_greedily_with_nested_impl_dep",
    )
    native.test_suite(
        name = name,
        tests = [
            ":mapping_to_transitive_deps_greedily_aggregates_custom_attrs",
            ":mapping_to_transitive_deps_greedily_filter_selects_only_matching_dep",
            ":mapping_to_transitive_deps_greedily_skips_nested_impl_deps",
        ],
    )
