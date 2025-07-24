import json
import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger()


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
        "--external_includes",
        nargs="*",
        help="Include paths available to the compiler for include statements pointing to headers from external targets."
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

    if len(sys.argv) == 2 and sys.argv[1].startswith("--param_file="):
        param_file = Path(sys.argv[1][len("--param_file=") :])
        args = parser.parse_args(param_file.read_text().splitlines())
    else:
        args = parser.parse_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)

    return args


def main(args: Namespace) -> int:
    log.debug(f"\nAnalyzing dependency '{args.target}'")
    log.debug(f"Output               '{args.output}'")
    log.debug(f"Header files         '{args.header_files}'")
    log.debug(f"Includes             '{args.includes}'")
    log.debug(f"Quote includes       '{args.quote_includes}'")
    log.debug(f"External includes    '{args.external_includes}'")
    log.debug(f"System includes      '{args.system_includes}'")
    log.debug(f"Defines              '{args.defines}'")

    output = {"target": args.target, "header_files": args.header_files}
    if args.includes is not None:
        output["includes"] = args.includes
    if args.quote_includes is not None:
        output["quote_includes"] = args.quote_includes
    if args.external_includes is not None:
        output["external_includes"] = args.external_includes
    if args.system_includes is not None:
        output["system_includes"] = args.system_includes
    if args.defines is not None:
        output["defines"] = args.defines

    with args.output.open(mode="w", encoding="utf-8") as out:
        out.write(json.dumps(output))

    return 0


if __name__ == "__main__":
    sys.exit(main(cli()))
