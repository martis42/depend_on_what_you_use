load("@rules_cc//cc:defs.bzl", "cc_library")
load("//dwyu/cc/cc_info_mapping/private:direct_deps.bzl", "mapping_to_direct_deps")
load("//dwyu/cc/cc_info_mapping/private:explicit.bzl", "explicit_mapping")
load("//dwyu/cc/cc_info_mapping/private:explicit_deps.bzl", "mapping_to_explicit_deps")
load("//dwyu/cc/cc_info_mapping/private:transitive_deps.bzl", "mapping_to_transitive_deps")
load(":custom_rules.bzl", "cc_info_with_custom_deps")
load(":direct_deps_test.bzl", "direct_deps_test_suite")
load(":explicit_deps_test.bzl", "explicit_deps_test_suite")
load(":explicit_mapping_test.bzl", "explicit_mapping_test_suite")
load(":to_canonical.bzl", "to_canonical")
load(":transitive_deps_test.bzl", "transitive_deps_test_suite")

#
# Tests
#

direct_deps_test_suite(name = "direct_deps_tests")

explicit_mapping_test_suite(name = "explicit_mapping_tests")

explicit_deps_test_suite(name = "explicit_deps_tests")

transitive_deps_test_suite(name = "transitive_deps_tests")

#
# Direct dependency mappings
#

mapping_to_direct_deps(
    name = "mapping_to_direct_deps",
    target = ":lib_with_dep",
)

mapping_to_direct_deps(
    name = "mapping_to_direct_deps_with_impl_dep",
    target = ":lib_with_impl_dep",
)

mapping_to_direct_deps(
    name = "mapping_to_direct_deps_with_non_cc_dep",
    target = ":lib_with_non_cc_dep",
)

mapping_to_direct_deps(
    name = "mapping_to_direct_deps_with_filter",
    filter = [to_canonical("//dwyu/cc/cc_info_mapping/private/test:dep_layer_1")],
    target = ":lib_with_two_deps",
)

#
# Transitive dependency mappings
#

mapping_to_transitive_deps(
    name = "mapping_to_transitive_deps",
    target = ":lib_with_dep",
)

mapping_to_transitive_deps(
    name = "mapping_to_transitive_deps_with_impl_dep",
    target = ":lib_with_impl_dep",
)

mapping_to_transitive_deps(
    name = "mapping_to_transitive_deps_with_non_cc_dep",
    target = ":lib_with_non_cc_dep",
)

mapping_to_transitive_deps(
    name = "mapping_to_transitive_deps_with_no_deps_attr",
    target = ":lib_with_custom_cc_dep",
)

mapping_to_transitive_deps(
    name = "mapping_to_transitive_deps_with_filter",
    filter = [to_canonical("//dwyu/cc/cc_info_mapping/private/test:dep_layer_1")],
    target = ":lib_with_two_deps",
)

#
# Explicit mappings
#

explicit_mapping(
    name = "mapping_to_explicit_deps",
    map_to = [
        ":dep_layer_1",
        ":dep_layer_2",
    ],
    target = ":lib_with_impl_dep",
)

#
# Explicit target mappings
#

mapping_to_explicit_deps(
    name = "mapping_to_explicit_direct_dep",
    mapped_targets = [to_canonical("//dwyu/cc/cc_info_mapping/private/test:dep_layer_1")],
    target = ":lib_with_two_deps",
)

mapping_to_explicit_deps(
    name = "mapping_to_explicit_transitive_dep",
    mapped_targets = [to_canonical("//dwyu/cc/cc_info_mapping/private/test:dep_layer_2")],
    target = ":lib_with_dep",
)

mapping_to_explicit_deps(
    name = "mapping_to_target_outside_dependency_tree_fails",
    mapped_targets = [to_canonical("//non/existing:dep")],
    tags = ["manual"],  # prevent this being analyzed outside the analysis test
    target = ":lib_with_dep",
)

mapping_to_explicit_deps(
    name = "mapping_to_explicit_deps_using_custom_rules",
    mapped_targets = [
        to_canonical("//dwyu/cc/cc_info_mapping/private/test:extra_dep"),
        to_canonical("//dwyu/cc/cc_info_mapping/private/test:lib_with_dep"),
    ],
    target = ":lib_with_custom_deps",
)

#
# Support targets
#

cc_library(
    name = "dep_layer_2",
    hdrs = ["dep_layer_2.h"],
)

cc_library(
    name = "dep_layer_1",
    hdrs = ["dep_layer_1.h"],
    deps = [":dep_layer_2"],
)

cc_library(
    name = "lib_with_dep",
    hdrs = ["lib_with_dep.h"],
    deps = [":dep_layer_1"],
)

cc_library(
    name = "extra_dep",
    hdrs = ["extra_dep.h"],
)

cc_library(
    name = "lib_with_two_deps",
    hdrs = ["lib_with_two_deps.h"],
    deps = [
        ":dep_layer_1",
        ":extra_dep",
    ],
)

cc_library(
    name = "lib_with_impl_dep",
    srcs = ["lib_with_impl_dep.cpp"],
    hdrs = ["lib_with_impl_dep.h"],
    implementation_deps = [":dep_layer_1"],
)

# genrule is used as a stand-in for any non-CcInfo target (e.g. sh_library);
# it is in the allow-list for cc_library.deps and does not provide CcInfo.
genrule(
    name = "non_cc_dep",
    outs = ["non_cc_dep_dummy.txt"],
    cmd = "touch $@",
)

cc_library(
    name = "lib_with_non_cc_dep",
    hdrs = ["lib_with_non_cc_dep.h"],
    deps = [":non_cc_dep"],
)

cc_info_with_custom_deps(
    name = "custom_cc_dep",
    hdrs = ["custom_dep.h"],
)

cc_library(
    name = "lib_with_custom_cc_dep",
    hdrs = ["lib_with_custom_cc_dep.h"],
    deps = [":custom_cc_dep"],
)

cc_info_with_custom_deps(
    name = "custom_cc_info_with_custom_deps",
    hdrs = ["custom_cc_info_with_custom_deps.h"],
    multiple_deps = [":lib_with_dep"],
    # Explicitly specify attributes not using targets as input to confirm our logic skips over them
    non_target_attr = "some_value",
    non_target_list_attr = [
        "value1",
        "value2",
    ],
    single_dep = ":extra_dep",
)

cc_library(
    name = "lib_with_custom_deps",
    hdrs = ["lib_with_custom_deps.h"],
    deps = [":custom_cc_info_with_custom_deps"],
)
