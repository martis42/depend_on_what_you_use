#!/usr/bin/env python3
import sys

from execute_tests_impl import (
    CompatibleVersions,
    ExpectedResult,
    TestCase,
    TestCmd,
    cli,
    main,
)

BAZEL_VERSIONS = [
    "4.0.0",
    "4.2.3",
    "5.0.0",
    "5.3.2",
    "6.0.0",
    "7.0.0-pre.20221212.2",
]

VERSION_SPECIFIC_ARGS = {
    "5.0.0": [
        "--incompatible_enforce_config_setting_visibility",
        "--incompatible_config_setting_private_default_visibility",
    ]
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
        name="unused_private_dep",
        compatible_versions=CompatibleVersions(min="5.0.0"),
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
        compatible_versions=CompatibleVersions(min="5.0.0"),
        cmd=TestCmd(
            target="//test/aspect/implementation_deps:proper_private_deps",
            aspect="//test/aspect/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="binary_with_implementation_deps_activated",
        compatible_versions=CompatibleVersions(min="5.0.0"),
        cmd=TestCmd(
            target="//test/aspect/implementation_deps:binary_using_foo",
            aspect="//test/aspect/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="test_with_implementation_deps_activated",
        compatible_versions=CompatibleVersions(min="5.0.0", max="6.9.9"),
        cmd=TestCmd(
            target="//test/aspect/implementation_deps:test_using_foo",
            aspect="//test/aspect/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="superfluous_public_dep",
        compatible_versions=CompatibleVersions(min="5.0.0"),
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
        compatible_versions=CompatibleVersions(min="4.1.0"),  # Does not compile with 4.0.0
        cmd=TestCmd(target="//test/aspect/complex_includes:all", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="complex_includes_in_ext_repo",
        compatible_versions=CompatibleVersions(min="4.1.0"),  # Does not compile with 4.0.0
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
        compatible_versions=CompatibleVersions(min="4.1.0"),
        cmd=TestCmd(target="//test/aspect/relative_includes/...", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    # Bazel 4.0.0 does not include the source files in the header file lists in CcInfo. Only the generated files at the
    # virtual paths are included, which does not suffice for our relative include logic. This has been fixed with Bazel
    # 4.1.0
    TestCase(
        name="relative_includes_for_bazel_400_part_1",
        compatible_versions=CompatibleVersions(max="4.0.0"),
        cmd=TestCmd(
            target="//test/aspect/relative_includes:normal_include",
            aspect=DEFAULT_ASPECT,
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="relative_includes_for_bazel_400_part_2",
        compatible_versions=CompatibleVersions(max="4.0.0"),
        cmd=TestCmd(
            target="//test/aspect/relative_includes:system_include",
            aspect=DEFAULT_ASPECT,
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="relative_includes_for_bazel_400_part_3",
        compatible_versions=CompatibleVersions(max="4.0.0"),
        cmd=TestCmd(
            target="//test/aspect/relative_includes:use_normal_include",
            aspect=DEFAULT_ASPECT,
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="relative_includes_for_bazel_400_part_4",
        compatible_versions=CompatibleVersions(max="4.0.0"),
        cmd=TestCmd(
            target="//test/aspect/relative_includes:use_system_include",
            aspect=DEFAULT_ASPECT,
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="simple_defines_use_foo_or_bar_default",
        cmd=TestCmd(target="//test/aspect/simple_defines:use_foo_or_bar", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="simple_defines_use_foo_or_bar_enable_foo",
        cmd=TestCmd(
            target="//test/aspect/simple_defines:use_foo_or_bar",
            aspect=DEFAULT_ASPECT,
            extra_args=["--//test/aspect/simple_defines:enable_foo"],
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="complex_defines_a_or_b",
        cmd=TestCmd(target="//test/aspect/complex_defines:a_or_b", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(
            success=False,
            unused_public_deps=["//test/aspect/complex_defines:a"],
            invalid_includes=["File='test/aspect/complex_defines/main.cpp', include='test/aspect/complex_defines/b.h'"],
        ),
    ),
]

if __name__ == "__main__":
    args = cli()
    sys.exit(
        main(args=args, test_cases=TESTS, test_versions=BAZEL_VERSIONS, version_specific_args=VERSION_SPECIFIC_ARGS)
    )
