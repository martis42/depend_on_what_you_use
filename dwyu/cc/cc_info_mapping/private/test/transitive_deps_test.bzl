load("@bazel_skylib//lib:unittest.bzl", "analysistest", "asserts")
load("//dwyu/cc/cc_info_mapping/private:providers.bzl", "DwyuRemappedCcInfo")

def _transitive_deps_are_aggregated_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    direct_headers = [h.basename for h in headers]

    expected_headers = ["lib.h", "dep_layer_1.h", "dep_layer_2.h"]
    asserts.equals(env, expected_headers, direct_headers)

    return analysistest.end(env)

transitive_deps_are_aggregated_test = analysistest.make(_transitive_deps_are_aggregated_test_impl)

def _implementation_deps_are_excluded_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = [h.basename for h in headers]

    expected_headers = ["lib_with_impl_dep.h"]
    asserts.equals(env, expected_headers, header_names)

    return analysistest.end(env)

implementation_deps_are_excluded_test = analysistest.make(_implementation_deps_are_excluded_test_impl)

def _non_cc_dep_is_skipped_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = [h.basename for h in headers]

    expected_headers = ["lib.h"]
    asserts.equals(env, expected_headers, header_names)

    return analysistest.end(env)

non_cc_dep_is_skipped_test = analysistest.make(_non_cc_dep_is_skipped_test_impl)

def _cc_dep_without_deps_attr_is_handled_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = [h.basename for h in headers]

    expected_headers = ["lib_with_custom_cc_dep.h", "custom_dep.h"]
    asserts.equals(env, expected_headers, header_names)

    return analysistest.end(env)

cc_dep_without_deps_attr_is_handled_test = analysistest.make(_cc_dep_without_deps_attr_is_handled_test_impl)

def transitive_deps_test_suite(name):
    transitive_deps_are_aggregated_test(
        name = "mapping_to_transitive_deps_finds_headers",
        target_under_test = ":mapping_to_transitive_deps",
    )
    implementation_deps_are_excluded_test(
        name = "mapping_to_transitive_deps_skips_impl_deps",
        target_under_test = ":mapping_to_transitive_deps_with_impl_dep",
    )
    non_cc_dep_is_skipped_test(
        name = "mapping_to_transitive_deps_skips_non_cc_deps",
        target_under_test = ":mapping_to_transitive_deps_with_non_cc_dep",
    )
    cc_dep_without_deps_attr_is_handled_test(
        name = "mapping_to_transitive_deps_skips_cc_dep_without_deps_attr",
        target_under_test = ":mapping_to_transitive_deps_with_no_deps_attr",
    )
    native.test_suite(
        name = name,
        tests = [
            ":mapping_to_transitive_deps_finds_headers",
            ":mapping_to_transitive_deps_skips_impl_deps",
            ":mapping_to_transitive_deps_skips_non_cc_deps",
            ":mapping_to_transitive_deps_skips_cc_dep_without_deps_attr",
        ],
    )
