import json
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, List


def cli():
    parser = ArgumentParser()
    parser.add_argument(
        "--workspace",
        metavar="PATH",
        required=True,
        help="Workspace for which DWYU reports are gathered and fixes are applied to the source code.",
    )
    parser.add_argument(
        "--buildozer",
        metavar="PATH",
        help="buildozer binary which shall be used by this script. "
        "If none is provided, it is expected to find buildozer on PATH.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't apply fixes. Report the buildozer commands and print the adapted BUILD files to stdout.",
    )
    parser.add_argument("--verbose", action="store_true", help="Announce intermediate steps.")

    return parser.parse_args()


def get_bazel_bin_dir(workspace: Path) -> Path:
    process = subprocess.run(["bazel", "info", "bazel-bin"], cwd=workspace, check=True, capture_output=True, text=True)
    return Path(process.stdout.strip())


def gather_reports(bazel_bin: Path) -> List[Path]:
    return list(bazel_bin.glob("**/*_dwyu_report.json"))


def make_base_cmd(buildozer: str, dry: bool) -> List[str]:
    cmd = [buildozer]
    if dry:
        cmd.append("-stdout")
    return cmd


def perform_fixes(workspace: Path, report: Path, buildozer: str, dry: bool = False, verbose=False):
    with open(report, encoding="utf-8") as report_in:
        content = json.load(report_in)
        target = content["analyzed_target"]
        unused_deps = content["unused_dependencies"]
        base_cmd = make_base_cmd(buildozer=buildozer, dry=dry)
        if unused_deps:
            deps_str = " ".join(unused_deps)
            cmd = base_cmd + [f"remove deps {deps_str}", target]
            if dry or verbose:
                print(f"Buildozer command: {cmd}")
            subprocess.run(cmd, cwd=workspace, check=True)


def main(args: Any) -> int:
    """
    This script expects that the user has invoked DWYU in the given workspace and by doing so generated DYWU report
    files in the output path.

    The script expects "bazel" to be available on PATH.
    """
    buildozer = args.buildozer if args.buildozer else "buildozer"

    bin_dir = get_bazel_bin_dir(args.workspace)
    if args.verbose:
        print(f"Bazel-bin directory: '{bin_dir}'")

    reports = gather_reports(bin_dir)
    for report in reports:
        if args.verbose:
            print(f"Report File '{report}'")
        perform_fixes(
            workspace=args.workspace, report=report, buildozer=buildozer, dry=args.dry_run, verbose=args.verbose
        )


if __name__ == "__main__":
    cli_args = cli()
    sys.exit(main(cli_args))
