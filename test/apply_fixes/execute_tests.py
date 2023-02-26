#!/usr/bin/env python3
import logging
from argparse import ArgumentParser
from sys import exit

from execution_logic import main

logging.basicConfig(format="%(message)s", level=logging.INFO)


def cli():
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output of test runs.")
    parser.add_argument("--list", "-l", action="store_true", help="List all available test cases and return.")
    parser.add_argument(
        "--test",
        "-t",
        nargs="+",
        help="Run the specified test cases. Substrings will match against all test names including them.",
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = cli()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    exit(main(requested_tests=args.test, list_tests=args.list))
