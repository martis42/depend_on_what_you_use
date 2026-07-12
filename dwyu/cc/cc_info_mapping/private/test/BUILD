load("@rules_cc//cc:defs.bzl", "cc_library")
load("//dwyu/cc/cc_info_mapping/private:direct_deps.bzl", "mapping_to_direct_deps")
load("//dwyu/cc/cc_info_mapping/private:explicit.bzl", "explicit_mapping")
load("//dwyu/cc/cc_info_mapping/private:transitive_deps.bzl", "mapping_to_transitive_deps")
load(":custom_rules.bzl", "cc_info_without_deps")
load(":direct_deps_test.bzl", "direct_deps_test_suite")
load(":explicit_mapping_test.bzl", "explicit_mapping_test_suite")
load(":transitive_deps_test.bzl", "transitive_deps_test_suite")

#
# Tests
#

direct_deps_test_suite(name = "direct_deps_tests")

explicit_mapping_test_suite(name = "explicit_mapping_tests")

transitive_deps_test_suite(name = "transitive_deps_tests")

#
# Direct dependency mappings
#

mapping_to_direct_deps(
    name = "mapping_to_direct_deps",
    target = ":lib_with_deps",
)

mapping_to_direct_deps(
    name = "mapping_to_direct_deps_with_impl_dep",
    target = ":lib_with_impl_dep",
)

mapping_to_direct_deps(
    name = "mapping_to_direct_deps_with_non_cc_dep",
    target = ":lib_with_non_cc_dep",
)

#
# Transitive dependency mappings
#

mapping_to_transitive_deps(
    name = "mapping_to_transitive_deps",
    target = ":lib_with_deps",
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
    name = "lib_with_deps",
    hdrs = ["lib.h"],
    deps = [":dep_layer_1"],
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
    hdrs = ["lib.h"],
    deps = [":non_cc_dep"],
)

cc_info_without_deps(
    name = "custom_cc_dep",
    hdrs = ["custom_dep.h"],
)

cc_library(
    name = "lib_with_custom_cc_dep",
    hdrs = ["lib_with_custom_cc_dep.h"],
    deps = [":custom_cc_dep"],
)
