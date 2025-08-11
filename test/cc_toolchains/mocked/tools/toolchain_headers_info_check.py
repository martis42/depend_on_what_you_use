from __future__ import annotations

import json
import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger()


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
        "--expected_header_files",
        metavar="FILE",
        nargs="*",
        required=True,
        help="We expect those header files to be in the file provided via '--input'. Order does not matter.",
    )
    parser.add_argument(
        "--expected_include_statements",
        metavar="FILE",
        nargs="*",
        required=True,
        help="We expect those include statements to be in the file provided via '--input'. Order does not matter.",
    )

    return parser.parse_args()


def main(args: Namespace) -> int:
    log.info(f"Analyzing input file '{args.input}'")

    input_data = args.input.read_text()
    data = json.loads(input_data)

    sorted_header_files = sorted(data["header_files"])
    sorted_include_statements = sorted(data["include_statements"])

    correct_header_files = sorted_header_files == sorted(args.expected_header_files)
    correct_include_statements = sorted_include_statements == sorted(args.expected_include_statements)

    if correct_header_files and correct_include_statements:
        log.info("Test succeeded")
        return 0

    log.error("ERROR: Input does not match expectations")
    if not correct_header_files:
        log.error(f"  Input    header_files : {sorted_header_files}")
        log.error(f"  Expected header_files : {sorted(args.expected_header_files)}")
    if not correct_include_statements:
        log.error(f"  Input    include_statements : {sorted_include_statements}")
        log.error(f"  Expected include_statements : {sorted(args.expected_include_statements)}")
    return 1


if __name__ == "__main__":
    sys.exit(main(cli()))
