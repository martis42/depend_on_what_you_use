from __future__ import annotations

import contextlib
import json
import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

logging.basicConfig(format="%(message)s", level=logging.DEBUG)
log = logging.getLogger(__name__)


def cli() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument(
        "--built_in_include_directories",
        metavar="PATH",
        type=Path,
        nargs="*",
        help="""
        Directories below any number of header files could be located.
        Mostly used by the non hermetic parts of the CC toolchain.
        """,
    )
    parser.add_argument(
        "--toolchain_files",
        metavar="FILE",
        type=Path,
        nargs="*",
        help="All files provided hermetically by the toolchain. Those are headers as well as libraries and tools.",
    )
    parser.add_argument(
        "--toolchain_include_directories",
        metavar="PATH",
        type=Path,
        nargs="*",
        help="Include directories provided to the compiler to discover the headers from the files provided via '--toolchain_files'.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        type=Path,
        help="Store all discovered headers in the specified file as list in json format.",
    )
    parser.add_argument(
        "--param_file",
        metavar="FILE",
        type=Path,
        help="""
        If the command line input would be too large, one can provide the arguments via a file.
        Overwrites all other parameters which might have provided via the CLI in parallel to '--param_file'.
        """,
    )

    args = parser.parse_args()
    if args.param_file:
        args = parser.parse_args(args.param_file.read_text().splitlines())

    return args


def is_relevant_file(file: Path) -> bool:
    if file.suffix in [".h", ".hh", ".hpp"]:
        return True

    # There are files without any suffix for the C++ standard includes (e.g. 'vector').
    # However, while we want to include them, we do not want hidden support files or tool binaries or directories.
    return not file.is_dir() and not file.name.startswith(".") and file.suffix == "" and file.parent.name != "bin"


def gather_built_in_headers(include_directories: list[Path]) -> list[str]:
    headers = []
    for ip in include_directories:
        headers.extend([str(f.relative_to(ip)) for f in ip.glob("**/*") if is_relevant_file(f)])
    return headers


def gather_toolchain_headers(toolchain_files: list[Path], toolchain_include_dirs: list[Path]) -> list[str]:
    headers = []
    for file in toolchain_files:
        if is_relevant_file(file):
            for include_dir in toolchain_include_dirs:
                # Properly testing with 'is_relative_to' requires Python >= 3.9
                with contextlib.suppress(ValueError):
                    headers.append(str(file.relative_to(include_dir)))
    return headers


def main(args: Namespace) -> int:
    built_in_headers = gather_built_in_headers(args.built_in_include_directories)
    log.debug(f"Discovered built in headers: {len(built_in_headers)}")

    toolchain_headers = gather_toolchain_headers(
        toolchain_files=args.toolchain_files, toolchain_include_dirs=args.toolchain_include_directories
    )
    log.debug(f"Discovered toolchain headers: {len(toolchain_headers)}")

    # We do not want to report duplicate values
    all_headers = list(set(built_in_headers + toolchain_headers))
    log.debug(f"Total unique headers: {len(all_headers)}")

    with args.output.open(mode="wt", encoding="utf-8") as output:
        json.dump(all_headers, output)

    return 0


if __name__ == "__main__":
    sys.exit(main(cli()))
