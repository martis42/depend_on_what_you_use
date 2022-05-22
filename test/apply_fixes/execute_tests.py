#!/usr/bin/env python3
import sys
from argparse import ArgumentParser

from execute_tests_impl import TestCase, main

CUSTOM_OUTPUT_BASE = "/tmp/dwyu/apply_fixes_tests/custom_output_base"

TESTS = [
    TestCase(
        name="remove_unused_dependency",
        path="test/apply_fixes/unused_dependencies",
        target="//:main",
        expected_deps=["//:used"],
    ),
    # Executing the automatic fixes tool with "--dry-run" must not remove the unused dependency
    TestCase(
        name="dry_run_ignores_the_unused_dependecy",
        path="test/apply_fixes/unused_dependencies",
        target="//:main",
        apply_fixes_extra_args=["--dry-run"],
        expected_deps=["//:unused", "//:used"],
    ),
    TestCase(
        name="fail_on_missing_report_files",
        path="test/apply_fixes/unused_dependencies",
        target="//:main",
        # Skip the report generation
        dwyu_extra_args=["--nobuild"],
        expected_deps=[],
        expected_exception="returned non-zero exit status 1",
    ),
    TestCase(
        name="use_custom_output_base",
        path="test/apply_fixes/unused_dependencies",
        target="//:main",
        dwyu_extra_startup_args=[f"--output_base={CUSTOM_OUTPUT_BASE}"],
        apply_fixes_extra_args=[f"--bazel-bin={CUSTOM_OUTPUT_BASE}"],
        expected_deps=["//:used"],
    ),
    TestCase(
        name="use_convenience_symlinks",
        path="test/apply_fixes/unused_dependencies",
        target="//:main",
        dwyu_extra_args=["--compilation_mode=dbg"],
        apply_fixes_extra_args=["--use-convenience-symlinks"],
        expected_deps=["//:used"],
    ),
]


def cli():
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output of test runs.")
    parser.add_argument("--test", "-t", nargs="+", help="Run the specified test cases.")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    sys.exit(main(args=cli(), test_cases=TESTS))
