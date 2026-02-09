#!/usr/bin/env python3
import logging
import sys
from argparse import ArgumentParser, Namespace
from os import chdir
from pathlib import Path

# Allow importing test support code. Relative imports do not work in our case.
# We do this centrally here, so all code we import while executing this knows the extended PYTHONPATH
# ruff: noqa: E402
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from test.apply_fixes.execution_logic import main

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

    # Ensure we can invoke the script from various places
    chdir(Path(__file__).parent)

    sys.exit(main(requested_tests=args.test, list_tests=args.list))
