from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from dwyu.cc_toolchain_headers.private.gather_cc_toolchain_headers import extract_include_paths_from_gcc_like_output


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--input",
        metavar="FILE",
        type=Path,
        help="TBD",
    )
    parser.add_argument(
        "--file",
        metavar="FILE",
        type=Path,
        help="TBD",
    )
    parser.add_argument(
        "--toolchain_headers_info",
        metavar="FILE",
        type=Path,
        help="TBD",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        type=Path,
        help="TBD",
    )
    return parser.parse_args()


def extract_direct_include_statements(text: str) -> list[Path]:
    included_path = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(". "):
            included_path.append(Path(line.split(". ")[1]))

    return included_path


def is_relative_to(root: Path, sub: Path) -> bool:
    """
    pathlib version of this is not available before Python 3.9
    """
    return root == sub or sub in root.parents


def normalize_string_path(path: str) -> str:
    """
    We do not want to use pathlib because we don't want absolute paths
    """
    if not path:
        return ""

    normalized_path = path
    while ".." in normalized_path:
        if normalized_path.startswith("../"):
            normalized_path = normalized_path.replace("../", "", 1)
            _, _, normalized_path = normalized_path.partition("/")
        else:
            front, _, back = normalized_path.partition("/../")
            if "/" in front:
                front = front.rsplit("/", 1)[0]
                normalized_path = front + "/" + back
            else:
                normalized_path = back

    return normalized_path


def main(args: Namespace) -> int:
    """
    TBD
    Preprocessor output doc https://gcc.gnu.org/onlinedocs/cpp/Preprocessor-Output.html
    """
    toolchain_headers_info = json.loads(args.toolchain_headers_info.read_text())
    toolchain_header_files = set(toolchain_headers_info["header_files"])

    pp_output = args.input.read_text()

    # print("---------------")
    # print(output)
    # print("---------------")

    search_paths = extract_include_paths_from_gcc_like_output(pp_output)

    # print("#########")
    # print("\n".join(str(sp) for sp in search_paths))
    # print("#########")

    included_paths = extract_direct_include_statements(pp_output)
    normalized_included_paths = [normalize_string_path(str(ip)) for ip in included_paths]

    # print("+++++++")
    # print("\n".join(str(ip) for ip in included_paths))
    # print("+++++++")

    # print("-------------")
    # print("\n".join(str(ip) for ip in normalized_included_paths))
    # print("-------------")

    # We cannot distinguish between file relative includes and includes relative to include path when looking at pre-preprocessed output!!
    # Thus, we have to change the complete logic away from include statements to file paths

    # LEARNINGS
    # 1) We cannot use logic based on "include statements" as they appear in the code. The preprocessed information does not allow to distinguish between file relative includes and includes relative to the workspace root. All include statements are given as path relative to the compiler binary.
    # 2) We cannot take 'cc_toolchain.all_files' as input here. This does not work for non hermetic toolchains. Thus, we need to expand upon the DWYU toolchain info mechanism, which also has to provide a path to all toolchain paths, not just possible include statements

    # TODO
    # extend DWYU toolchain info, distinguish between absolute and relative paths to distinguish between system and hermetic stuff.
    # Take this as input here and compare included files to toolchain files
    # if is in toolchain files -> ignore
    # is not in toolchain files -> provided by dynamic target

    included_user_headers = [nip for nip in normalized_included_paths if nip not in toolchain_header_files]
    included_user_headers = list(set(included_user_headers))
    # for ip in included_paths:
    #     if ip not in toolchain_header_files:
    #         included_user_headers.append(ip)

    # print("<<<<<<<<<<<<<<<<<<<<<<<<")
    # print("\n".join(inc for inc in included_user_headers))
    # print("<<<<<<<<<<<<<<<<<<<<<<<<")

    args.output.write_text(
        json.dumps({"file": str(args.file), "included_headers": included_user_headers}), encoding="utf-8"
    )

    # return 1
    return 0


if __name__ == "__main__":
    cli_args = cli()
    sys.exit(main(cli_args))
