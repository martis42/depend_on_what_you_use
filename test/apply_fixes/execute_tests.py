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
    )
]


def cli():
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output of test runs.")
    parser.add_argument("--test", "-t", nargs="+", help="Run the specified test cases.")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    sys.exit(main(args=cli(), test_cases=TESTS))
