import json
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from dwyu.aspect.private.analyze_includes_new.lib import (
    aggregate_preprocessed_includes,
    evaluate_includes,
    get_system_under_inspection,
)


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--publicly_included_header",
        metavar="FILE",
        nargs="*",
        type=Path,
        help="Information about the header files included in the public files of the target under inspection.",
    )
    parser.add_argument(
        "--privately_included_header",
        metavar="FILE",
        nargs="*",
        type=Path,
        help="Information about the header files included in the private files of the target under inspection.",
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
    # parser.add_argument(
    #     "--ignored_includes_config",
    #     metavar="FILE",
    #     type=Path,
    #     help="Config file in Json format specifying which include paths and patterns shall be ignored by the analysis.",
    # )
    parser.add_argument(
        "--implementation_deps_available",
        action="store_true",
        help="""
        If this Bazel 5.0 feature is available, then check if some dependencies could be private instead of public.
        Meaning headers from them are only used in the private files.""",
    )
    parser.add_argument(
        "--toolchain_headers_info",
        metavar="FILE",
        type=Path,
        help="Json file with a list of all include statements available through the Bazel CC toolchain.",
    )
    return parser.parse_args()


def main(args: Namespace) -> int:
    # ignored_includes = get_ignored_includes(
    #     config_file=args.ignored_includes_config, toolchain_headers_info=args.toolchain_headers_info
    # )

    print("--------------")
    for x in args.publicly_included_header:
        print(x)
        print(x.read_text())
    print("--------------")
    for x in args.privately_included_header:
        print(x)
        print(x.read_text())
    print("--------------")

    cc_toolchain_info = json.loads(args.toolchain_headers_info.read_text())
    cc_toolchain_headers = set(cc_toolchain_info["header_files"])

    system_under_inspection = get_system_under_inspection(
        target_under_inspection=args.target_under_inspection,
        deps=args.deps,
        impl_deps=args.implementation_deps,
    )
    all_includes_from_public = aggregate_preprocessed_includes(
        # preprocessed_includes=args.public_files, ignored_includes=ignored_includes
        preprocessed_includes=args.publicly_included_header
    )
    all_includes_from_private = aggregate_preprocessed_includes(
        # preprocessed_includes=args.public_files, ignored_includes=ignored_includes
        preprocessed_includes=args.privately_included_header
    )

    result = evaluate_includes(
        public_includes=all_includes_from_public,
        private_includes=all_includes_from_private,
        system_under_inspection=system_under_inspection,
        ensure_private_deps=args.implementation_deps_available,
        toolchain_headers=cc_toolchain_headers,
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
