import json
import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List

logging.basicConfig(format="%(message)s", level=logging.INFO)


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--target", required=True, type=str, help="Target which is being analyzed.")
    parser.add_argument("--output", required=True, type=Path, help="Stores the analysis in this file.")
    parser.add_argument("--header_files", required=True, nargs="*", help="Header files associated with the target.")
    parser.add_argument(
        "--system_includes",
        required=True,
        nargs="*",
        help="System include directories defined by the target under inspection",
    )
    parser.add_argument("--bin_dir", required=True, type=str, help="Bazel bin output directory.")
    parser.add_argument(
        "--defines",
        nargs="*",
        help="Defines for this target."
        " Only relevant when analyzing the target under inspection itself. This is irrelevant for its dependencies.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print debugging output")

    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    return args


def include_paths_from_file(file: str, system_includes: List[str], bin_dir: str, is_external: bool) -> List[str]:
    if "_virtual_includes" in file:
        # Header files available through a virtual include directories are given via the pattern:
        # <pkg_dir_in_bazel_out>/_virtual_includes/<target_name>/<include_path_available_to_user>
        return [file.split("_virtual_includes/", 1)[1].split("/", 1)[1]]

    includes_from_system_paths = []
    if system_includes:
        for si in system_includes:
            si_path = si + "/"
            if file.startswith(si_path):
                includes_from_system_paths.append(file.split(si_path, 1)[1])

    # TODO investigate why returning early. Using absolute path relative to workspace root should always be possible
    if includes_from_system_paths:
        return includes_from_system_paths

    if is_external:
        # TODO is relying on 'external' working given the flags not using 'external' in runfiles trees?
        # Header files available through a virtual include directories are given via the pattern:
        # external/<external_workspace_name>/<include_path_available_to_user>
        return [file.split("external/", 1)[1].split("/", 1)[1]]

    # Generated code
    if file.startswith(bin_dir):
        return [file.split(f"{bin_dir}/", 1)[1]]

    # Default case for dependencies from within the own workspace not using any include path manipulation
    return [file]


def get_include_paths(files: List[str], system_includes: List[str], bin_dir: str, is_external: bool) -> List[str]:
    include_paths = []
    for file in files:
        include_paths.extend(
            include_paths_from_file(
                file=file, system_includes=system_includes, bin_dir=bin_dir, is_external=is_external
            )
        )
    return include_paths


def filter_files(files: List[str], is_external: bool) -> List[str]:
    # TODO move this logic into the analyzer, as here it is a surprising impl detail
    # The file list is used to resolve relative includes, which we don't do for external dependencies
    if is_external:
        return []
    return files


def is_external(target: str) -> bool:
    """
    Targets from external workspaces follow the pattern '@<workspace_name>//..' whereas targets from the own workspace
    start with '@//...' or the short form '//...'.
    """
    return not target.startswith(("@//", "//"))


def main(args: Namespace) -> int:
    logging.debug(f"\nAnalyzing dependency '{args.target}'")
    logging.debug(f"Output               '{args.output}'")
    logging.debug(f"Header files         '{args.header_files}'")
    logging.debug(f"System includes      '{args.system_includes}'")
    logging.debug(f"Bazel bin dir        '{args.bin_dir}'")

    output = {"target": args.target}
    is_external_target = is_external(args.target)
    output["header_files"] = filter_files(files=args.header_files, is_external=is_external_target)
    output["include_paths"] = get_include_paths(
        files=args.header_files,
        system_includes=args.system_includes,
        bin_dir=args.bin_dir,
        is_external=is_external_target,
    )
    if args.defines is not None:
        output["defines"] = args.defines

    with open(args.output, mode="w", encoding="utf-8") as out:
        out.write(json.dumps(output))

    return 0


if __name__ == "__main__":
    sys.exit(main(cli()))
