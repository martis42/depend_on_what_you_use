import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from dwyu.aspect.private.analyze_includes.evaluate_includes import evaluate_includes
from dwyu.aspect.private.analyze_includes.parse_config import get_ignored_includes
from dwyu.aspect.private.analyze_includes.parse_source import get_relevant_includes_from_files
from dwyu.aspect.private.analyze_includes.system_under_inspection import get_system_under_inspection


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--public_files",
        required=True,
        metavar="FILE",
        nargs="*",
        type=Path,
        help="All public source files of the target under inspection.",
    )
    parser.add_argument(
        "--private_files",
        required=True,
        metavar="FILE",
        nargs="*",
        type=Path,
        help="All private source files of the target under inspection.",
    )
    parser.add_argument(
        "--target_under_inspection",
        required=True,
        metavar="FILE",
        type=Path,
        help="Information about target under inspection.",
    )
    parser.add_argument(
        "--deps",
        required=True,
        metavar="FILE",
        nargs="*",
        type=Path,
        help="Information about dependencies.",
    )
    parser.add_argument(
        "--implementation_deps",
        required=True,
        metavar="FILE",
        nargs="*",
        type=Path,
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
        "--toolchain_headers_info",
        metavar="FILE",
        type=Path,
        help="Json file with a list of all include statements available through the Bazel CC toolchain.",
    )
    parser.add_argument(
        "--implementation_deps_available",
        action="store_true",
        help="""
        If this Bazel 5.0 feature is available, then check if some dependencies could be private instead of public.
        Meaning headers from them are only used in the private files.""",
    )
    parser.add_argument(
        "--no_preprocessor",
        action="store_true",
        help="""
        Do not use the preprocessor to analyze files. Is much faster but also less correct.
        Do not use this unless you have a performance problems and are sure the missing correctness is not hurting you.
        """,
    )
    return parser.parse_args()


def main(args: Namespace) -> int:
    ignored_includes = get_ignored_includes(
        config_file=args.ignored_includes_config, toolchain_headers_info=args.toolchain_headers_info
    )

    system_under_inspection = get_system_under_inspection(
        target_under_inspection=args.target_under_inspection,
        deps=args.deps,
        impl_deps=args.implementation_deps,
    )
    all_includes_from_public = get_relevant_includes_from_files(
        files=args.public_files,
        ignored_includes=ignored_includes,
        defines=system_under_inspection.defines,
        include_paths=system_under_inspection.include_paths,
        no_preprocessor=args.no_preprocessor,
    )
    all_includes_from_private = get_relevant_includes_from_files(
        files=args.private_files,
        ignored_includes=ignored_includes,
        defines=system_under_inspection.defines,
        include_paths=system_under_inspection.include_paths,
        no_preprocessor=args.no_preprocessor,
    )

    result = evaluate_includes(
        public_includes=all_includes_from_public,
        private_includes=all_includes_from_private,
        system_under_inspection=system_under_inspection,
        ensure_private_deps=args.implementation_deps_available,
    )
    result.report = args.report

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(result.to_json(), encoding="utf-8")

    if not result.is_ok():
        print(result.to_str())  # noqa: T201
        return 1

    return 0


if __name__ == "__main__":
    cli_args = cli()
    sys.exit(main(cli_args))
