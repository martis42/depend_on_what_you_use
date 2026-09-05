load("@bazel_skylib//lib:unittest.bzl", "analysistest", "asserts")
load("//dwyu/cc/cc_info_mapping/private:providers.bzl", "DwyuRemappedCcInfo")

def _explicit_direct_target_is_mapped_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = [header.basename for header in headers]

    asserts.equals(env, ["lib_with_two_deps.h", "dep_layer_1.h"], header_names)

    return analysistest.end(env)

explicit_direct_target_is_mapped_test = analysistest.make(_explicit_direct_target_is_mapped_test_impl)

def _explicit_transitive_target_is_mapped_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = [header.basename for header in headers]

    asserts.equals(env, ["lib_with_dep.h", "dep_layer_2.h"], header_names)

    return analysistest.end(env)

explicit_transitive_target_is_mapped_test = analysistest.make(_explicit_transitive_target_is_mapped_test_impl)

def _target_outside_dependency_tree_fails_test_impl(ctx):
    env = analysistest.begin(ctx)
    asserts.expect_failure(env, "Some 'mapped_targets' were not found in the dependency tree")
    return analysistest.end(env)

target_outside_dependency_tree_fails_test = analysistest.make(
    _target_outside_dependency_tree_fails_test_impl,
    expect_failure = True,
)

def _targets_reached_by_custom_dependency_attrs_are_mapped_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = [header.basename for header in headers]

    asserts.equals(env, ["extra_dep.h", "lib_with_custom_deps.h", "lib_with_dep.h"], sorted(header_names))

    return analysistest.end(env)

targets_reached_by_custom_dependency_attrs_are_mapped_test = analysistest.make(_targets_reached_by_custom_dependency_attrs_are_mapped_test_impl)

def explicit_deps_test_suite(name):
    explicit_direct_target_is_mapped_test(
        name = "mapping_to_explicit_deps_maps_direct_dep",
        target_under_test = ":mapping_to_explicit_direct_dep",
    )
    explicit_transitive_target_is_mapped_test(
        name = "mapping_to_explicit_deps_maps_transitive_dep",
        target_under_test = ":mapping_to_explicit_transitive_dep",
    )
    target_outside_dependency_tree_fails_test(
        name = "mapping_to_explicit_deps_target_outside_dependency_tree_fails",
        target_under_test = ":mapping_to_target_outside_dependency_tree_fails",
    )
    targets_reached_by_custom_dependency_attrs_are_mapped_test(
        name = "mapping_to_explicit_deps_maps_custom_rules",
        target_under_test = ":mapping_to_explicit_deps_using_custom_rules",
    )
    native.test_suite(
        name = name,
        tests = [
            ":mapping_to_explicit_deps_maps_direct_dep",
            ":mapping_to_explicit_deps_maps_transitive_dep",
            ":mapping_to_explicit_deps_target_outside_dependency_tree_fails",
            ":mapping_to_explicit_deps_maps_custom_rules",
        ],
    )
