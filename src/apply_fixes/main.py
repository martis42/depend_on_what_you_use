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
        workspace is provided, we assume we are running from within the workspace for which the DWYU reports have been
        generated and determine the workspace root automatically.
        By default the Bazel output directory containing the DWYU report files is deduced by following the 'bazel-bin'
        convenience symlink.""",
    )
    parser.add_argument(
        "--use-bazel-info",
        const="fastbuild",
        choices=["dbg", "fastbuild", "opt"],
        nargs="?",
        help="""
        Don't follow the convenience symlinks to reach the Bazel output directory containing the DWYU reports. Instead,
        use 'bazel info' to deduce the output directory.
        This option accepts an optional argument specifying the compilation mode which was used to generate the DWYU
        report files.
        Using this option is recommended if the convenience symlinks do not exist, don't follow the default
        naming scheme or do not point to the Bazel output directory containing the DWYU reports.""",
    )
    parser.add_argument(
        "--bazel-bin",
        metavar="PATH",
        help="""
        Path to the bazel-bin directory inside which the DWYU reports are located.
        Using this option is recommended if neither the convenience symlinks nor the 'bazel info' command are suited to
        deduce the Bazel output directory containing the DWYU report files.""",
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
    # TODO extra buildozer args to control flags like '-delete_with_comments' or '-shorten_labels'
    parser.add_argument("--verbose", action="store_true", help="Announce intermediate steps.")

    return parser.parse_args()


class Summary:
    def __init__(self) -> None:
        self.succesful_fixes = []
        self.failed_fixes = []
        self.fixes_without_effect = []

    def add_command(self, cmd: List[str], buildozer_result: int) -> None:
        if buildozer_result == 0:
            self.succesful_fixes.append(cmd)
        elif buildozer_result == 2:
            self.failed_fixes.append(cmd)
        elif buildozer_result == 3:
            self.fixes_without_effect.append(cmd)
        else:
            raise Exception(
                f"Running buildozer command '{cmd}' failed with the unexpected return code: {buildozer_result}"
            )

    # restricting the type to instances of the own class seems to be not possible with Python 3.6
    def extend(self, other: Any) -> Any:
        self.succesful_fixes.extend(other.succesful_fixes)
        self.failed_fixes.extend(other.failed_fixes)
        self.fixes_without_effect.extend(other.fixes_without_effect)

    def print_summary(self) -> None:
        print(f"\nSuccesful fixes: {len(self.succesful_fixes)}")

        if self.failed_fixes:
            print(
                """
WARNING Some buildozer commands failed!
Common causes for this can be:
- The workspace has changed since the DWYU report files have been generated and thus some targets no longer exist.
- The target which is supposed to be fixed is not written directly in a BUILD file, but created by a macro.

Failed commands:"""
            )
            print("\n".join(f"- {x}" for x in self.failed_fixes))

        if self.fixes_without_effect:
            print(
                """
WARNING Some buildozer commands did not create a change!
Common causes for this can be:
- You are executing the apply fixes script multiple times on the same report file.
- The script is trying to remove an aliased target. DWYU is only aware of the resolved target, which buildozer cannot
  connect to the alias name in the dependency list.

Commands without effect:"""
            )
            print("\n".join(f"- {x}" for x in self.fixes_without_effect))


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

    if main_args.use_bazel_info:
        process = subprocess.run(
            ["bazel", "info", f"--compilation_mode={main_args.use_bazel_info}", "bazel-bin"],
            cwd=workspace_root,
            check=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return Path(process.stdout.strip())

    bazel_bin_link = workspace_root / "bazel-bin"
    if not bazel_bin_link.is_symlink():
        print(f"ERROR: convenience symlink '{bazel_bin_link}' does not exist or is not a symlink.")
        sys.exit(1)
    return bazel_bin_link.resolve()


def gather_reports(bazel_bin: Path) -> List[Path]:
    return list(bazel_bin.glob("**/*_dwyu_report.json"))


def make_base_cmd(buildozer: str, dry: bool) -> List[str]:
    cmd = [buildozer]
    if dry:
        cmd.append("-stdout")
    return cmd


def execute_cmd(cmd: List[str], workspace: Path, summary: Summary, dry: bool, verbose: bool) -> None:
    if dry or verbose:
        print(f"Executing buildozer command: {cmd}")
    process = subprocess.run(cmd, cwd=workspace, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    summary.add_command(cmd=cmd, buildozer_result=process.returncode)


def perform_fixes(workspace: Path, report: Path, buildozer: str, dry: bool = False, verbose: bool = False) -> Summary:
    summary = Summary()

    with open(report, encoding="utf-8") as report_in:
        content = json.load(report_in)
        target = content["analyzed_target"]
        unused_public_deps = content["unused_public_dependencies"]
        unused_private_deps = content["unused_private_dependencies"]
        base_cmd = make_base_cmd(buildozer=buildozer, dry=dry)
        if unused_public_deps:
            deps_str = " ".join(unused_public_deps)
            cmd = base_cmd + [f"remove deps {deps_str}", target]
            execute_cmd(cmd=cmd, workspace=workspace, summary=summary, dry=dry, verbose=verbose)
        if unused_private_deps:
            deps_str = " ".join(unused_private_deps)
            cmd = base_cmd + [f"remove implementation_deps {deps_str}", target]
            execute_cmd(cmd=cmd, workspace=workspace, summary=summary, dry=dry, verbose=verbose)

    return summary


def main(args: Any) -> int:
    """
    This script expects that the user has invoked DWYU in the given workspace beforehand and by doing so generated DYWU
    report files in the output path.
    Running this script multiple times on the same report files will not break anything, but cause a lot of warnings,
    since all issues are already fixed. Always execute the DWYU aspect to generate fresh report files before executing
    this script.

    Beware that there are limits on what buildozer can achieve. Buildozer works on a limited set of information, since
    it looks at BUILD files before macro and alias expansion:
    - If targets are generated by macros buildozer cannot edit them.
    - The DWYU aspect runs after alias expansion and thus reports the actual names instead of the alias names. However,
      only the alias name is visible to buildozer in a BUILD file in the dependencies of a target.

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

    overall_summary = Summary()
    for report in reports:
        if args.verbose:
            print(f"Processing report file '{report}'")
        summary = perform_fixes(
            workspace=workspace, report=report, buildozer=buildozer, dry=args.dry_run, verbose=args.verbose
        )
        overall_summary.extend(summary)

    overall_summary.print_summary()

    return 0


if __name__ == "__main__":
    cli_args = cli()
    sys.exit(main(cli_args))
