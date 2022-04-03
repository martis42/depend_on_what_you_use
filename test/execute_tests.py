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
    "5.1.0",
    "6.0.0-pre.20220310.1",
]

VERSION_SPECIFIC_ARGS = {
    "5.0.0": [
        "--incompatible_enforce_config_setting_visibility",
        "--incompatible_config_setting_private_default_visibility",
    ]
}

DEFAULT_ASPECT = "//test:aspect.bzl%dwyu_default_aspect"

TESTS = [
    TestCase(
        name="custom_config",
        cmd=TestCmd(target="//test/custom_config:foo", aspect="//test/custom_config:aspect.bzl%custom_config_aspect"),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="unused_dep",
        cmd=TestCmd(target="//test/unused_dep:main", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=False, unused_deps=["//test/unused_dep:foo"]),
    ),
    TestCase(
        name="use_transitive_deps",
        cmd=TestCmd(target="//test/using_transitive_dep:main", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(
            success=False,
            invalid_includes=["File='test/using_transitive_dep/main.cpp', include='test/using_transitive_dep/foo.h'"],
        ),
    ),
    TestCase(
        name="use_external_dependencies",
        cmd=TestCmd(target="//test/external_repo:use_external_libs", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="proper implementation_deps",
        compatible_versions=CompatibleVersions(min="5.0.0", max="5.9.9"),
        cmd=TestCmd(
            target="//test/implementation_deps:proper_private_deps",
            aspect="//test/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        ),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="superfluous public_dep",
        compatible_versions=CompatibleVersions(min="5.0.0", max="5.9.9"),
        cmd=TestCmd(
            target="//test/implementation_deps:superfluous_public_dep",
            aspect="//test/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        ),
        expected=ExpectedResult(success=False, deps_which_should_be_private=["//test/implementation_deps:foo"]),
    ),
    TestCase(
        name="generated_code",
        cmd=TestCmd(target="//test/generated_code:foo", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    # Make sure headers from own lib are discovered correctly
    TestCase(
        name="system_includes_lib",
        cmd=TestCmd(target="//test/includes:includes", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="system_includes_use_lib",
        cmd=TestCmd(target="//test/includes:use_includes", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    # Make sure headers from own lib are discovered correctly
    TestCase(
        name="virtual_includes_add_prefix_lib",
        cmd=TestCmd(target="//test/virtual_includes:prefixed", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="virtual_includes_use_add_prefix_lib",
        cmd=TestCmd(target="//test/virtual_includes:use_prefixed", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    # Make sure headers from own lib are discovered correctly
    TestCase(
        name="virtual_includes_strip_prefix_lib",
        cmd=TestCmd(target="//test/virtual_includes:stripped", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="virtual_includes_use_strip_prefix_lib",
        cmd=TestCmd(target="//test/virtual_includes:use_stripped", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="valid",
        cmd=TestCmd(target="//test/valid:bar", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="recursive_disabled",
        cmd=TestCmd(target="//test/recursion:main", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="recursive_fail_transitively",
        cmd=TestCmd(target="//test/recursion:main", aspect="//test/recursion:aspect.bzl%recursive_aspect"),
        expected=ExpectedResult(success=False, unused_deps=["//test/recursion:e"]),
    ),
    TestCase(
        name="rule_direct_success",
        cmd=TestCmd(target="//test/recursion:dwyu_direct_main"),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="rule_recursive_failure",
        cmd=TestCmd(target="//test/recursion:dwyu_recursive_main"),
        expected=ExpectedResult(success=False, unused_deps=["//test/recursion:e"]),
    ),
    TestCase(
        name="complex_includes",
        compatible_versions=CompatibleVersions(min="4.1.0"),  # Does not compile with 4.0.0
        cmd=TestCmd(target="//test/complex_includes:all"),
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
        cmd=TestCmd(target="//test/platforms/..."),
        expected=ExpectedResult(success=True),
    ),
    TestCase(
        name="invalid_dependency_through_alias",
        cmd=TestCmd(target="//test/alias:use_a_transitively", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(
            success=False,
            invalid_includes=["File='test/alias/use_a_and_b.cpp', include='test/alias/a.h'"],
        ),
    ),
    TestCase(
        name="unused_dependency_through_alias",
        cmd=TestCmd(target="//test/alias:unused_dependency", aspect=DEFAULT_ASPECT),
        # The aspect does not see the alias, but only the resolved actual dependency
        expected=ExpectedResult(success=False, unused_deps=["//test/alias:lib_a"]),
    ),
    TestCase(
        name="dependency_through_alias",
        cmd=TestCmd(target="//test/alias:use_a_directly", aspect=DEFAULT_ASPECT),
        expected=ExpectedResult(success=True),
    ),
]

if __name__ == "__main__":
    args = cli()
    sys.exit(
        main(args=args, test_cases=TESTS, test_versions=BAZEL_VERSIONS, version_specific_args=VERSION_SPECIFIC_ARGS)
    )
