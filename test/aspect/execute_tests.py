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
    "4.2.2",
    "5.0.0",
    "5.1.1",
    "6.0.0-pre.20220630.1",
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
        name="custom_config_full",
        cmd=TestCmd(
            target="//test/aspect/custom_config:use_multiple_arcane_headers",
            aspect="//test/aspect/custom_config:aspect.bzl%full_custom_config_aspect",
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="custom_config_extra_ignore_include_paths",
        cmd=TestCmd(
            target="//test/aspect/custom_config:use_arcane_header_and_vector",
            aspect="//test/aspect/custom_config:aspect.bzl%extra_ignore_include_paths_aspect",
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="custom_config_ignore_include_paths",
        cmd=TestCmd(
            target="//test/aspect/custom_config:use_arcane_header",
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
        name="unused_dep",
        cmd=TestCmd(target="//test/aspect/unused_dep:main", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=False, unused_deps=["//test/aspect/unused_dep:foo"]),
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
        name="proper implementation_deps",
        compatible_versions=CompatibleVersions(min="5.0.0", max="5.9.9"),
        cmd=TestCmd(
            target="//test/aspect/implementation_deps:proper_private_deps",
            aspect="//test/aspect/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="superfluous public_dep",
        compatible_versions=CompatibleVersions(min="5.0.0", max="5.9.9"),
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
        expected=ExpectedResult(success=False, unused_deps=["//test/aspect/recursion:e"]),
    ),
    TestCase(
        name="rule_direct_success",
        cmd=TestCmd(target="//test/aspect/recursion:dwyu_direct_main"),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="rule_recursive_failure",
        cmd=TestCmd(target="//test/aspect/recursion:dwyu_recursive_main"),
        expected=ExpectedResult(success=False, unused_deps=["//test/aspect/recursion:e"]),
    ),
    TestCase(
        name="complex_includes",
        compatible_versions=CompatibleVersions(min="4.1.0"),  # Does not compile with 4.0.0
        cmd=TestCmd(target="//test/aspect/complex_includes:all"),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="complex_includes_in_ext_repo",
        compatible_versions=CompatibleVersions(min="4.1.0"),  # Does not compile with 4.0.0
        cmd=TestCmd(target="@complex_includes_repo//..."),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="incompatible_platforms",
        cmd=TestCmd(target="//test/aspect/platforms/..."),
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
        expected=ExpectedResult(success=False, unused_deps=["//test/aspect/alias:lib_a"]),
    ),
    TestCase(
        name="dependency_through_alias",
        cmd=TestCmd(target="//test/aspect/alias:use_a_directly", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="valid_interface_dep",
        compatible_versions=CompatibleVersions(min="6.0.0"),
        cmd=TestCmd(
            target="//test/aspect/interface_deps:valid_deps",
            aspect="//test/aspect/interface_deps:aspect.bzl%interface_deps_aspect",
            extra_args=["--experimental_cc_interface_deps"],
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="invalid_interface_dep",
        compatible_versions=CompatibleVersions(min="6.0.0"),
        cmd=TestCmd(
            target="//test/aspect/interface_deps:invalid_deps",
            aspect="//test/aspect/interface_deps:aspect.bzl%interface_deps_aspect",
            extra_args=["--experimental_cc_interface_deps"],
        ),
        expected=ExpectedResult(success=False, deps_which_should_be_private=["//test/aspect/interface_deps:b"]),
    ),
]

if __name__ == "__main__":
    args = cli()
    sys.exit(
        main(args=args, test_cases=TESTS, test_versions=BAZEL_VERSIONS, version_specific_args=VERSION_SPECIFIC_ARGS)
    )
