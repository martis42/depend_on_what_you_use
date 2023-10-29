import json
import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

logging.basicConfig(format="%(message)s", level=logging.INFO)


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--target", required=True, type=str, help="Target which is being analyzed.")
    parser.add_argument("--output", required=True, type=Path, help="Stores the analysis in this file.")
    parser.add_argument("--header_files", required=True, nargs="*", help="Header files associated with the target.")
    parser.add_argument(
        "--includes",
        nargs="*",
        help="Include paths available to the compiler."
        " Only relevant when analyzing the target under inspection itself. This is irrelevant for dependencies.",
    )
    parser.add_argument(
        "--quote_includes",
        nargs="*",
        help="Include paths available to the compiler for quoted include statements."
        " Only relevant when analyzing the target under inspection itself. This is irrelevant for dependencies.",
    )
    parser.add_argument(
        "--system_includes",
        nargs="*",
        help="Include paths available to the compiler for system include statements"
        " Only relevant when analyzing the target under inspection itself. This is irrelevant for dependencies.",
    )
    parser.add_argument(
        "--defines",
        nargs="*",
        help="Defines for this target."
        " Only relevant when analyzing the target under inspection itself. This is irrelevant for dependencies.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print debugging output")

    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    return args


def main(args: Namespace) -> int:
    logging.debug(f"\nAnalyzing dependency '{args.target}'")
    logging.debug(f"Output               '{args.output}'")
    logging.debug(f"Header files         '{args.header_files}'")
    logging.debug(f"Includes             '{args.includes}'")
    logging.debug(f"Quote includes       '{args.quote_includes}'")
    logging.debug(f"System includes      '{args.system_includes}'")

    output = {"target": args.target, "header_files": args.header_files}
    if args.includes is not None:
        output["includes"] = args.includes
    if args.quote_includes is not None:
        output["quote_includes"] = args.quote_includes
    if args.system_includes is not None:
        output["system_includes"] = args.system_includes
    if args.defines is not None:
        output["defines"] = args.defines

    with open(args.output, mode="w", encoding="utf-8") as out:
        out.write(json.dumps(output))

    return 0


if __name__ == "__main__":
    sys.exit(main(cli()))
