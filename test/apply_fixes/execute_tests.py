#!/usr/bin/env python3
from argparse import ArgumentParser
from sys import exit

from src.test_execution import main


def cli():
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output of test runs.")
    parser.add_argument("--list", "-l", action="store_true", help="List all available test cases and return.")
    parser.add_argument(
        "--test",
        "-t",
        nargs="+",
        help="Run the specified test cases. Can provide substrings which will match against all strings including them.",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = cli()
    exit(main(requested_tests=args.test, list_tests=args.list, verbose=args.verbose))
