from __future__ import annotations

import contextlib
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
        "--include_directories",
        metavar="PATH",
        type=Path,
        nargs="*",
        help="Directories below which any number of header files could be located.",
    )
    parser.add_argument(
        "--gcc_like_include_paths_info",
        metavar="FILE",
        type=Path,
        help="TBD",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        type=Path,
        help="Store all discovered headers in the specified file as list in json format.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output for debugging",
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

    if args.include_directories and args.gcc_like_include_paths_info:
        log.error(
            "ERROR: Cannot use '--include_directories' and 'gcc_like_include_paths_info' together. Choose one of both."
        )
        sys.exit(1)

    return args


def is_relevant_file(file: Path) -> bool:
    # TODO are there other postifxes and what about capslock?
    if file.suffix in [".h", ".hh", ".hpp"]:
        return True

    # There are files without any suffix for the C++ standard includes (e.g. 'vector').
    # However, while we want to include them, we do not want hidden support files or tool binaries or directories.
    return not file.is_dir() and not file.name.startswith(".") and file.suffix == "" and file.parent.name != "bin"


def gather_built_in_headers(include_directories: list[Path]) -> list[str]:
    headers = []
    for id in include_directories:
        headers.extend([str(f.relative_to(id)) for f in id.glob("**/*") if is_relevant_file(f)])
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
    if args.verbose:
        log.setLevel(logging.DEBUG)

    if args.gcc_like_include_paths_info:
        include_paths = []

        data = args.gcc_like_include_paths_info.read_text()
        found_include_paths_section = False
        for raw_line in data.splitlines():
            line = raw_line.strip()

            if line == '#include "..." search starts here:':
                found_include_paths_section = True
                continue
            if line == "#include <...> search starts here:":
                continue
            if line == "End of search list.":
                break

            if found_include_paths_section:
                include_paths.append(Path(line))
    else:
        include_paths = args.include_directories

    log.debug(f"Discovered CC toolchain include paths: {len(include_paths)}")
    log.debug("\n".join([f"- {ip}" for ip in include_paths]))

    headers = gather_built_in_headers(include_paths)
    log.debug(f"Discovered toolchain headers: {len(headers)}")

    with args.output.open(mode="wt", encoding="utf-8") as output:
        json.dump(headers, output)

    return 0


if __name__ == "__main__":
    sys.exit(main(cli()))
