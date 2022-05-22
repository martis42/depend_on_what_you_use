import json
import subprocess
import sys
from argparse import ArgumentParser
from os import environ
from pathlib import Path
from typing import Any, List

# Bazel sets this environment for 'bazel run' to document the workspace root
WORKSPACE_ENV_VAR = "BUILD_WORKSPACE_DIRECTORY"


def cli():
    parser = ArgumentParser()
    parser.add_argument(
        "--workspace",
        metavar="PATH",
        help="""
        Workspace for which DWYU reports are gathered and fixes are applied to the source code. If no dedicated
        workspace is provided, we assume we are running from within the workspace for which the DWYU report have been
        generated and determine the workspace root automatically.
        If neither '--use-convenience-symlinks' nor '--bazel-bin' are provided, the bazel-bin directory is deduced
        automatically. This deduction assumes the DWYU reports have been generated with the fastbuild compilation mode.
        """,
    )
    parser.add_argument(
        "--use-convenience-symlinks",
        action="store_true",
        help="""
        Follow the convenience symlinks at the workspace root to find the output directory containing the DWYU reports.
        """,
    )
    parser.add_argument(
        "--bazel-bin",
        metavar="PATH",
        help="""
        Path to the bazel-bin directory inside which the DWYU reports are located. Use this option when you have to
        generate the report files with another compilation mode than fastbuild or when you use a custom output base.""",
    )
    parser.add_argument(
        "--buildozer",
        metavar="PATH",
        help="""
        buildozer binary which shall be used by this script. If none is provided, it is expected to find buildozer on
        PATH.""",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't apply fixes. Report the buildozer commands and print the adapted BUILD files to stdout.",
    )
    parser.add_argument("--verbose", action="store_true", help="Announce intermediate steps.")

    return parser.parse_args()


def get_workspace(main_args: Any) -> Path:
    if main_args.workspace:
        return Path(main_args.workspace)

    workspace_root = environ.get(WORKSPACE_ENV_VAR)
    if not workspace_root:
        print(
            "ERROR:"
            f" No workspace was explicitly provided and environment variable '{WORKSPACE_ENV_VAR}' is not available."
        )
    return Path(workspace_root)


def get_bazel_bin_dir(main_args: Any, workspace_root: Path) -> Path:
    if main_args.bazel_bin:
        return Path(main_args.bazel_bin)

    if main_args.use_convenience_symlinks:
        bazel_bin_link = workspace_root / "bazel-bin"
        if not bazel_bin_link.is_symlink():
            print(f"ERROR: convenience symlink '{bazel_bin_link}' does not exist or is not a symlink.")
            sys.exit(1)
        return bazel_bin_link.resolve()

    process = subprocess.run(
        ["bazel", "info", "bazel-bin"],
        cwd=workspace_root,
        check=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
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

    workspace = get_workspace(args)
    if args.verbose:
        print(f"Workspace: '{workspace}'")

    bin_dir = get_bazel_bin_dir(main_args=args, workspace_root=workspace)
    if args.verbose:
        print(f"Bazel-bin directory: '{bin_dir}'")

    reports = gather_reports(bin_dir)
    if not reports:
        print("ERROR: Did not find any DWYU report files.")
        print("Did you forget to run DWYU beforehand?")
        print(
            "By default this tool looks for DWYU report files in the output directory for a 'fastbuild' DWYU execution."
            " If you want to use another output directory, have a look at the apply_fixes CLI options via '--help'."
        )
        return 1

    for report in reports:
        if args.verbose:
            print(f"Report File '{report}'")
        perform_fixes(workspace=workspace, report=report, buildozer=buildozer, dry=args.dry_run, verbose=args.verbose)

    return 0


if __name__ == "__main__":
    cli_args = cli()
    sys.exit(main(cli_args))
