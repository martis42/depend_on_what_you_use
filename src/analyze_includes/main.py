import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from src.analyze_includes.evaluate_includes import evaluate_includes
from src.analyze_includes.parse_config import get_ignored_includes
from src.analyze_includes.parse_source import get_relevant_includes_from_files
from src.analyze_includes.system_under_inspection import get_system_under_inspection


def cli():
    parser = ArgumentParser()
    parser.add_argument(
        "--public-files", metavar="PATH", nargs="+", help="All public files of the target under inspection."
    )
    parser.add_argument(
        "--private-files", metavar="PATH", nargs="+", help="All private files of the target under inspection."
    )
    parser.add_argument(
        "--headers-info", metavar="PATH", help="Json file containing information about all relevant header files."
    )
    parser.add_argument("--report", metavar="FILE", type=Path, help="Report result into this file.")
    parser.add_argument(
        "--ignored-includes-config",
        metavar="FILE",
        type=Path,
        help="Config file in Json format specifying which include paths and patterns shall be ignored by the analysis.",
    )
    parser.add_argument(
        "--implementation-deps-available",
        action="store_true",
        help="""
        If this Bazel 5.0 feature is available, then check if some dependencies could be private instead of public.
        Meaning headers from them are only used in the private files.""",
    )

    args = parser.parse_args()
    if not args.public_files and not args.private_files:
        print("You have to provide at least one of the arguments '--public-files' and '--private-files'")
        sys.exit(1)

    return args


def main(args: Namespace) -> int:
    ignored_includes = get_ignored_includes(args.ignored_includes_config)
    system_under_inspection = get_system_under_inspection(args.headers_info)

    all_includes_from_public = get_relevant_includes_from_files(
        files=args.public_files,
        ignored_includes=ignored_includes,
        compile_flags=system_under_inspection.compile_flags,
    )
    all_includes_from_private = get_relevant_includes_from_files(
        files=args.private_files,
        ignored_includes=ignored_includes,
        compile_flags=system_under_inspection.compile_flags,
    )

    result = evaluate_includes(
        public_includes=all_includes_from_public,
        private_includes=all_includes_from_private,
        system_under_inspection=system_under_inspection,
        ensure_private_deps=args.implementation_deps_available,
    )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    with open(args.report, mode="w", encoding="utf-8") as report:
        report.write(result.to_json())

    if not result.is_ok():
        print(result.to_str())
        return 1

    return 0


if __name__ == "__main__":
    cli_args = cli()
    sys.exit(main(cli_args))
