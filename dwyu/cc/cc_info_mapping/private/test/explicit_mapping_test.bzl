load("@bazel_skylib//lib:unittest.bzl", "analysistest", "asserts")
load("//dwyu/cc/cc_info_mapping/private:providers.bzl", "DwyuRemappedCcInfo")

def _all_mapped_targets_headers_are_included_test_impl(ctx):
    env = analysistest.begin(ctx)

    headers = analysistest.target_under_test(env)[DwyuRemappedCcInfo].cc_info.compilation_context.direct_headers
    header_names = [h.basename for h in headers]

    expected_headers = ["lib_with_impl_dep.h", "dep_layer_1.h", "dep_layer_2.h"]
    asserts.equals(env, expected_headers, header_names)

    return analysistest.end(env)

all_mapped_targets_headers_are_included_test = analysistest.make(_all_mapped_targets_headers_are_included_test_impl)

def explicit_mapping_test_suite(name):
    all_mapped_targets_headers_are_included_test(
        name = "mapping_to_explicit_deps_finds_headers",
        target_under_test = ":mapping_to_explicit_deps",
    )
    native.test_suite(
        name = name,
        tests = [
            ":mapping_to_explicit_deps_finds_headers",
        ],
    )
