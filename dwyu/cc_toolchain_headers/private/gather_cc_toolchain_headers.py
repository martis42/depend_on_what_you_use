from __future__ import annotations

import json
import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger()


HEADER_EXTENSIONS = [".h", ".hh", ".hp", ".hpp", ".hxx", ".h++", ".tcc"]


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


def is_relevant_file(file: Path, include_dir: Path) -> bool:
    # Ignore directories and hidden files
    if file.is_dir() or file.name.startswith("."):
        return False

    if file.suffix.lower() in HEADER_EXTENSIONS:
        return True

    # There are files without any suffix for the C++ standard includes (e.g. 'vector').
    # Those files are always directly below an include directory.
    return file.suffix == "" and file.parent == include_dir


def gather_toolchain_headers(include_directories: list[Path]) -> tuple[list[str], list[str]]:
    include_statements = []
    header_files = []
    for include_dir in include_directories:
        include_statements.extend(
            [
                str(file.relative_to(include_dir))
                for file in include_dir.glob("**/*")
                if is_relevant_file(file=file, include_dir=include_dir)
            ]
        )
        header_files.extend(
            [str(file) for file in include_dir.glob("**/*") if is_relevant_file(file=file, include_dir=include_dir)]
        )

    return list(set(header_files)), list(set(include_statements))


def extract_include_paths_from_gcc_like_output(text: str) -> list[Path]:
    include_paths = []

    found_include_paths_section = False
    for raw_line in text.splitlines():
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

    return include_paths


def main(args: Namespace) -> int:
    if args.verbose:
        log.setLevel(logging.DEBUG)

    if args.gcc_like_include_paths_info:
        include_paths = extract_include_paths_from_gcc_like_output(text=args.gcc_like_include_paths_info.read_text())
    else:
        include_paths = args.include_directories

    log.debug(f"Searching CC toolchain include paths: {len(include_paths)}")
    log.debug("\n".join([f"- {ip}" for ip in include_paths]))

    header_files, include_statements = gather_toolchain_headers(include_paths)
    log.debug(f"Discovered toolchain header files       : {len(header_files)}")
    log.debug(f"Discovered toolchain include statements : {len(include_statements)}")

    with args.output.open(mode="wt", encoding="utf-8") as output:
        indent = 2 if args.verbose else None
        json.dump({"header_files": header_files, "include_statements": include_statements}, output, indent=indent)

    return 0


if __name__ == "__main__":
    sys.exit(main(cli()))
