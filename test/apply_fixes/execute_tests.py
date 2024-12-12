#!/usr/bin/env python3
import logging
import sys
from argparse import ArgumentParser, Namespace

from execution_logic import main

logging.basicConfig(format="%(message)s", level=logging.INFO)


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output of test runs.")
    parser.add_argument("--list", "-l", action="store_true", help="List all available test cases and return.")
    parser.add_argument(
        "--test",
        "-t",
        nargs="+",
        help="Run the specified test cases. Substrings will match against all test names including them.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = cli()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    sys.exit(main(requested_tests=args.test, list_tests=args.list))
