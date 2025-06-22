from __future__ import annotations

import json
import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger(__name__)


def cli() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument(
        "--input",
        metavar="FILE",
        required=True,
        type=Path,
        help="File containing discovered toolchain headers we compare to the provided list of expected discovered headers",
    )
    parser.add_argument(
        "--expected_headers",
        metavar="FILE",
        nargs="*",
        required=True,
        help="We expect this content in '--input'. Order does not matter.",
    )

    return parser.parse_args()


def main(args: Namespace) -> int:
    log.info(f"Analyzing input file '{args.input}'")

    input_data = args.input.read_text()
    data = json.loads(input_data)

    sorted_input = sorted(data)
    sorted_expected = sorted(args.expected_headers)

    if sorted_input == sorted_expected:
        log.info("Test succeeded")
        return 0

    log.error("ERROR: Input does not match expectations")
    log.error(f"  Input    : {sorted_input}")
    log.error(f"  Expected : {sorted_expected}")
    return 1


if __name__ == "__main__":
    sys.exit(main(cli()))
