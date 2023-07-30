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
        "--public_files",
        required=True,
        metavar="FILE",
        nargs="*",
        help="All public source files of the target under inspection.",
    )
    parser.add_argument(
        "--private_files",
        required=True,
        metavar="FILE",
        nargs="*",
        help="All private source files of the target under inspection.",
    )
    parser.add_argument(
        "--target_under_inspection",
        required=True,
        metavar="FILE",
        help="Information about target under inspection.",
    )
    parser.add_argument(
        "--deps",
        required=True,
        metavar="FILE",
        nargs="*",
        help="Information about dependencies.",
    )
    parser.add_argument(
        "--implementation_deps",
        required=True,
        metavar="FILE",
        nargs="*",
        help="Information about implementation dependencies.",
    )
    parser.add_argument(
        "--report",
        required=True,
        metavar="FILE",
        type=Path,
        help="Report result into this file.",
    )
    parser.add_argument(
        "--ignored_includes_config",
        metavar="FILE",
        type=Path,
        help="Config file in Json format specifying which include paths and patterns shall be ignored by the analysis.",
    )
    parser.add_argument(
        "--implementation_deps_available",
        action="store_true",
        help="""
        If this Bazel 5.0 feature is available, then check if some dependencies could be private instead of public.
        Meaning headers from them are only used in the private files.""",
    )
    return parser.parse_args()


def main(args: Namespace) -> int:
    ignored_includes = get_ignored_includes(args.ignored_includes_config)

    system_under_inspection = get_system_under_inspection(
        target_under_inspection=args.target_under_inspection,
        deps=args.deps,
        implementation_deps=args.implementation_deps,
    )
    all_includes_from_public = get_relevant_includes_from_files(
        files=args.public_files, ignored_includes=ignored_includes, defines=system_under_inspection.defines
    )
    all_includes_from_private = get_relevant_includes_from_files(
        files=args.private_files, ignored_includes=ignored_includes, defines=system_under_inspection.defines
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
