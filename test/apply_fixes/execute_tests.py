#!/usr/bin/env python3
import sys
from argparse import ArgumentParser

from execute_tests_impl import TestCase, main

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
]


def cli():
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output of test runs.")
    parser.add_argument("--test", "-t", nargs="+", help="Run the specified test cases.")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    sys.exit(main(args=cli(), test_cases=TESTS))
