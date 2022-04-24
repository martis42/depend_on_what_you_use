import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from src.analyze_includes.evaluate_includes import evaluate_includes
from src.analyze_includes.get_dependencies import get_available_dependencies
from src.analyze_includes.parse_config import load_config
from src.analyze_includes.parse_source import get_relevant_includes_from_files
from src.analyze_includes.std_header import STD_HEADER


def cli():
    parser = ArgumentParser()
    parser.add_argument("--target", help="Target which is being analyzed.")
    parser.add_argument(
        "--public-files", metavar="PATH", nargs="+", help="All public files of the target under inspection."
    )
    parser.add_argument(
        "--private-files", metavar="PATH", nargs="+", help="All private files of the target under inspection."
    )
    parser.add_argument(
        "--headers-info", metavar="PATH", help="Json file containing information about all relevant header files."
    )
    parser.add_argument("--report", metavar="FILE", help="Report result into this file.")
    parser.add_argument(
        "--config",
        metavar="FILE",
        help="Config file in Json format overriting the attributes '--ignore-include-paths' "
        "and '--extra-ignore-include-paths'.",
    )
    parser.add_argument(
        "--implementation-deps-available",
        action="store_true",
        help="If this Bazel 5.0 feature is vailable, then check if some dependencies "
        "could be private instead of public. Meaning headers from them are only used in the private files.",
    )
    parser.add_argument(
        "--ignore-include-paths",
        metavar="PATH",
        nargs="*",
        help="By default all headers of the standard library are ignored. "
        "You can however also provide your own list of include paths to be ignored.",
    )
    parser.add_argument(
        "--extra-ignore-include-paths",
        metavar="PATH",
        nargs="+",
        help="By default all headers of the standard library are ignored. "
        "If you want to ignore further include paths, you can specify them here. "
        "If you provided a custom ignore list, the include paths here are added to it.",
    )

    args = parser.parse_args()
    if not args.public_files and not args.private_files:
        print("You have to provide at least one of the arguments '--public-files' and '--private-files'")
        sys.exit(1)

    if args.config and (args.ignore_include_paths or args.extra_ignore_include_paths):
        print("'--config' overwrites 'ignore-include-paths' and 'extra-ignore-include-paths'. Don't combine them")
        sys.exit(1)

    return args


def _get_ignored_includes(args: Any) -> set:
    ignored_includes = STD_HEADER if not args.ignore_include_paths else {args.ignore_include_paths}
    extra_ignored_includes = {args.extra_ignore_include_paths} if args.extra_ignore_include_paths else {}

    if args.config:
        config_ignored_includes, config_extra_ignored_includes = load_config(Path(args.config))
        if config_ignored_includes:
            ignored_includes = set(config_ignored_includes)
        if config_extra_ignored_includes:
            extra_ignored_includes = set(config_extra_ignored_includes)

    return ignored_includes.union(extra_ignored_includes)


def main(args: Any) -> int:
    ignored_includes = _get_ignored_includes(args)

    all_includes_from_public = get_relevant_includes_from_files(
        files=args.public_files, ignored_includes=ignored_includes
    )
    all_includes_from_private = get_relevant_includes_from_files(
        files=args.private_files, ignored_includes=ignored_includes
    )

    allowed_includes = get_available_dependencies(args.headers_info)

    result = evaluate_includes(
        target=args.target,
        public_includes=all_includes_from_public,
        private_includes=all_includes_from_private,
        dependencies=allowed_includes,
        ensure_private_deps=args.implementation_deps_available,
    )

    out = Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, mode="w", encoding="utf-8") as report:
        report.write(result.to_json())

    if not result.is_ok():
        print(result.to_str())
        return 1

    return 0


if __name__ == "__main__":
    cli_args = cli()
    sys.exit(main(cli_args))
