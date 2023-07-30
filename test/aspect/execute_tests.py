#!/usr/bin/env python3
import sys

from execute_tests_impl import (
    CompatibleVersions,
    ExpectedResult,
    TestCase,
    TestCmd,
    TestedVersions,
    cli,
    main,
)

# Test matrix. We don't combine each Bazel version with each Python version as there is no significant benefit. We
# manually define pairs which make sure each Bazel and Python version we care about is used at least once.
TESTED_VERSIONS = [
    TestedVersions(bazel="5.0.0", python="3.8.15"),
    TestedVersions(bazel="5.4.1", python="3.9.16"),
    TestedVersions(bazel="6.0.0", python="3.10.9"),
    TestedVersions(bazel="6.3.0", python="3.11.1"),
    TestedVersions(bazel="7.0.0-pre.20230710.5", python="3.11.1"),
]

# When Bazel 7.0.0 releases we have to look again at the flags and check if more flags are available
VERSION_SPECIFIC_ARGS = {
    "--incompatible_legacy_local_fallback=false": CompatibleVersions(min="5.0.0"),  # false is the forward path behavior
    "--incompatible_enforce_config_setting_visibility": CompatibleVersions(min="5.0.0"),
    "--incompatible_config_setting_private_default_visibility": CompatibleVersions(min="5.0.0"),
    "--incompatible_disable_target_provider_fields": CompatibleVersions(min="5.0.0"),
    "--incompatible_struct_has_no_methods": CompatibleVersions(min="5.0.0"),
    "--incompatible_use_platforms_repo_for_constraints": CompatibleVersions(min="5.0.0"),
    "--incompatible_disallow_empty_glob": CompatibleVersions(min="5.0.0"),
    "--incompatible_existing_rules_immutable_view": CompatibleVersions(min="5.0.0"),
    "--incompatible_no_implicit_file_export": CompatibleVersions(min="5.0.0"),
    "--incompatible_use_cc_configure_from_rules_cc": CompatibleVersions(min="5.0.0"),
    "--incompatible_default_to_explicit_init_py": CompatibleVersions(min="5.0.0"),
    "--incompatible_exclusive_test_sandboxed": CompatibleVersions(min="5.0.0"),
    "--incompatible_strict_action_env": CompatibleVersions(min="5.0.0"),
    "--incompatible_disable_starlark_host_transitions": CompatibleVersions(min="6.0.0"),
    "--incompatible_sandbox_hermetic_tmp": CompatibleVersions(min="6.0.0"),
    "--incompatible_check_testonly_for_output_files": CompatibleVersions(min="6.0.0"),
    "--incompatible_check_visibility_for_toolchains": CompatibleVersions(min="7.0.0"),
    # Theoretically interesting for our project, but Bazel itself does not adhere to it
    # "--incompatible_python_disallow_native_rules": CompatibleVersions(min="7.0.0"),
    # "--incompatible_disallow_struct_provider_syntax": CompatibleVersions(min="7.0.0"),
}

DEFAULT_ASPECT = "//test/aspect:aspect.bzl%dwyu_default_aspect"

TESTS = [
    TestCase(
        name="custom_config_extra_ignore_include_paths",
        cmd=TestCmd(
            target="//test/aspect/custom_config:use_arcane_header_and_vector",
            aspect="//test/aspect/custom_config:aspect.bzl%extra_ignore_include_paths_aspect",
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="custom_config_custom_ignore_include_paths",
        cmd=TestCmd(
            target="//test/aspect/custom_config:use_multiple_arcane_headers",
            aspect="//test/aspect/custom_config:aspect.bzl%ignore_include_paths_aspect",
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="custom_config_ignore_include_patterns",
        cmd=TestCmd(
            target="//test/aspect/custom_config:use_ignored_patterns",
            aspect="//test/aspect/custom_config:aspect.bzl%extra_ignore_include_patterns_aspect",
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="custom_config_include_not_covered_by_patterns",
        cmd=TestCmd(
            target="//test/aspect/custom_config:use_not_ignored_header",
            aspect="//test/aspect/custom_config:aspect.bzl%extra_ignore_include_patterns_aspect",
        ),
        expected=ExpectedResult(
            success=False,
            invalid_includes=[
                "File='test/aspect/custom_config/use_not_ignored_header.h', include='example_substring_matching_does_not_work_here.h'"
            ],
        ),
    ),
    TestCase(
        name="unused_dep",
        cmd=TestCmd(target="//test/aspect/unused_dep:main", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=False, unused_public_deps=["//test/aspect/unused_dep:foo"]),
    ),
    TestCase(
        name="unused_dep_skipped",
        cmd=TestCmd(target="//test/aspect/unused_dep:main_skipped", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="unused_private_dep",
        cmd=TestCmd(
            target="//test/aspect/unused_dep/implementation_deps:implementation_deps_lib",
            aspect="//test/aspect/unused_dep:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        ),
        expected=ExpectedResult(success=False, unused_private_deps=["//test/aspect/unused_dep:foo"]),
    ),
    TestCase(
        name="use_transitive_deps",
        cmd=TestCmd(target="//test/aspect/using_transitive_dep:main", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(
            success=False,
            invalid_includes=[
                "File='test/aspect/using_transitive_dep/main.cpp', include='test/aspect/using_transitive_dep/foo.h'"
            ],
        ),
    ),
    TestCase(
        name="use_external_dependencies",
        cmd=TestCmd(target="//test/aspect/external_repo:use_external_libs", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="proper_implementation_deps",
        cmd=TestCmd(
            target="//test/aspect/implementation_deps:proper_private_deps",
            aspect="//test/aspect/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="binary_with_implementation_deps_activated",
        cmd=TestCmd(
            target="//test/aspect/implementation_deps:binary_using_foo",
            aspect="//test/aspect/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="test_with_implementation_deps_activated",
        cmd=TestCmd(
            target="//test/aspect/implementation_deps:test_using_foo",
            aspect="//test/aspect/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="superfluous_public_dep",
        cmd=TestCmd(
            target="//test/aspect/implementation_deps:superfluous_public_dep",
            aspect="//test/aspect/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        ),
        expected=ExpectedResult(success=False, deps_which_should_be_private=["//test/aspect/implementation_deps:foo"]),
    ),
    TestCase(
        name="generated_code",
        cmd=TestCmd(target="//test/aspect/generated_code:foo", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    # Make sure headers from own lib are discovered correctly
    TestCase(
        name="system_includes_lib",
        cmd=TestCmd(target="//test/aspect/includes:includes", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="system_includes_use_lib",
        cmd=TestCmd(target="//test/aspect/includes:use_includes", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    # Make sure headers from own lib are discovered correctly
    TestCase(
        name="virtual_includes_add_prefix_lib",
        cmd=TestCmd(target="//test/aspect/virtual_includes:prefixed", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="virtual_includes_use_add_prefix_lib",
        cmd=TestCmd(target="//test/aspect/virtual_includes:use_prefixed", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    # Make sure headers from own lib are discovered correctly
    TestCase(
        name="virtual_includes_strip_prefix_lib",
        cmd=TestCmd(target="//test/aspect/virtual_includes:stripped", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="virtual_includes_use_strip_prefix_lib",
        cmd=TestCmd(target="//test/aspect/virtual_includes:use_stripped", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="valid",
        cmd=TestCmd(target="//test/aspect/valid:bar", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="recursive_disabled",
        cmd=TestCmd(target="//test/aspect/recursion:main", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="recursive_fail_transitively",
        cmd=TestCmd(
            target="//test/aspect/recursion:main", aspect="//test/aspect/recursion:aspect.bzl%recursive_aspect"
        ),
        expected=ExpectedResult(success=False, unused_public_deps=["//test/aspect/recursion:e"]),
    ),
    TestCase(
        name="rule_direct_success",
        cmd=TestCmd(target="//test/aspect/recursion:dwyu_direct_main"),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="rule_recursive_failure",
        cmd=TestCmd(target="//test/aspect/recursion:dwyu_recursive_main"),
        expected=ExpectedResult(success=False, unused_public_deps=["//test/aspect/recursion:e"]),
    ),
    TestCase(
        name="complex_includes",
        cmd=TestCmd(target="//test/aspect/complex_includes:all", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="complex_includes_in_ext_repo",
        cmd=TestCmd(target="@complex_includes_repo//...", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="incompatible_platforms",
        cmd=TestCmd(target="//test/aspect/platforms/...", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="invalid_dependency_through_alias",
        cmd=TestCmd(target="//test/aspect/alias:use_a_transitively", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(
            success=False,
            invalid_includes=["File='test/aspect/alias/use_a_and_b.cpp', include='test/aspect/alias/a.h'"],
        ),
    ),
    TestCase(
        name="unused_dependency_through_alias",
        cmd=TestCmd(target="//test/aspect/alias:unused_dependency", aspect=DEFAULT_ASPECT),
        # The aspect does not see the alias, but only the resolved actual dependency
        expected=ExpectedResult(success=False, unused_public_deps=["//test/aspect/alias:lib_a"]),
    ),
    TestCase(
        name="dependency_through_alias",
        cmd=TestCmd(target="//test/aspect/alias:use_a_directly", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="no_public_or_private_files_binary_link_shared",
        cmd=TestCmd(target="//test/aspect/shared_library:libfoo.so", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="relative_includes",
        cmd=TestCmd(target="//test/aspect/relative_includes/...", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="in_file_defines",
        cmd=TestCmd(
            target="//test/aspect/defines:in_file_defines",
            aspect=DEFAULT_ASPECT,
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="defines_from_bazel_target",
        cmd=TestCmd(
            target="//test/aspect/defines:defines_from_bazel_target",
            aspect=DEFAULT_ASPECT,
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="transitive_defines_from_bazel_target",
        cmd=TestCmd(
            target="//test/aspect/defines:transitive_defines_from_bazel_target",
            aspect=DEFAULT_ASPECT,
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="depend_on_tree_artifact",
        cmd=TestCmd(
            target="//test/aspect/tree_artifact:use_tree_artifact",
            aspect=DEFAULT_ASPECT,
        ),
        expected=ExpectedResult(success=True),
    ),
    # FIXMe this is a brittle test as it depends on '--compilation_mode'
    TestCase(
        name="analyze_tree_artifact",
        cmd=TestCmd(
            target="//test/aspect/tree_artifact:tree_artifact_library",
            aspect=DEFAULT_ASPECT,
        ),
        expected=ExpectedResult(
            success=False,
            invalid_includes=[
                "File='bazel-out/k8-fastbuild/bin/test/aspect/tree_artifact/sources.cc/tree_lib.cc', include='test/aspect/tree_artifact/some_lib.h'"
            ],
        ),
    ),
]

if __name__ == "__main__":
    args = cli()
    if not args:
        sys.exit(1)
    sys.exit(
        main(args=args, test_cases=TESTS, tested_versions=TESTED_VERSIONS, version_specific_args=VERSION_SPECIFIC_ARGS)
    )
