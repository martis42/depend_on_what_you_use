"""
Apply the findings of a DWYU report to the BUILD file of the analyzed target with buildozer.

Parallel fix actions may edit the same BUILD file. The tool serializes the edits through a lock on the package
directory. Buildozer may replace the BUILD file instead of writing to it, which makes a lock on the BUILD file itself
ineffective.
"""

import fcntl
import json
import logging
import os
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = logging.getLogger()

BUILDOZER_NO_CHANGES = 3


def cli() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--report", type=Path, required=True, help="DWYU report of the target")
    parser.add_argument(
        "--header_owners",
        type=Path,
        required=True,
        help="File with a '<header> <owner>' line for each header in the dependency closure of the target",
    )
    parser.add_argument(
        "--source_file",
        type=Path,
        required=True,
        help="Source file of the target, used to resolve the workspace root from the execution root",
    )
    parser.add_argument("--buildozer", type=Path, required=True, help="Buildozer executable")
    parser.add_argument("--output", type=Path, required=True, help="Stamp file written after applying the fixes")
    return parser.parse_args()


def main_repo_label(label: str) -> str | None:
    """
    DWYU reports labels as `str(label)`, which is `@@//pkg:name` for targets of the main repository.
    """
    repo, sep, rest = label.partition("//")
    if not sep or repo not in ("", "@", "@@"):
        return None
    return f"//{rest}"


def read_header_owners(file: Path) -> dict[str, str]:
    owners = {}
    for line in file.read_text(encoding="utf-8").splitlines():
        header, owner = line.split(" ", 1)
        owners[header] = owner
    return owners


def workspace_root(source_file: Path) -> Path:
    """
    The execution root links each top level directory of the main repository into the workspace.
    """
    return source_file.resolve().parents[len(source_file.parts) - 1]


def missing_deps(report: dict, header_owners: dict[str, str]) -> list[str]:
    deps = set()
    for key in ("public_includes_without_dep", "private_includes_without_dep"):
        for headers in report[key].values():
            for header in headers:
                if owner := header_owners.get(header):
                    deps.add(owner)
                else:
                    log.warning(f"No target in the dependency closure of {report['analyzed_target']} owns '{header}'")
    return sorted(deps)


def run_buildozer(buildozer: Path, task: str, target: str, workspace: Path) -> None:
    # The path of the buildozer executable is relative to the execution root
    command = [str(buildozer.resolve()), task, target]
    process = subprocess.run(command, cwd=workspace, check=False, capture_output=True, text=True)
    if process.returncode not in (0, BUILDOZER_NO_CHANGES):
        log.error(f"Buildozer command {command} failed:\n{process.stderr}")
        sys.exit(1)


def main(args: Namespace) -> int:
    report = json.loads(args.report.read_text(encoding="utf-8"))
    target = main_repo_label(report["analyzed_target"])
    if not target:
        log.error(f"Target {report['analyzed_target']} is not part of the main repository")
        return 1

    add = [dep for dep in missing_deps(report, read_header_owners(args.header_owners)) if main_repo_label(dep)]
    remove = [label for dep in report["unused_deps"] if (label := main_repo_label(dep))]

    if add or remove:
        workspace = workspace_root(args.source_file)
        package_dir = workspace / target.removeprefix("//").split(":", 1)[0]
        lock_fd = os.open(package_dir, os.O_RDONLY)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            log.info(f"Fixing dependencies of {target}")
            if remove:
                run_buildozer(args.buildozer, task=f"remove deps {' '.join(remove)}", target=target, workspace=workspace)
            if add:
                run_buildozer(args.buildozer, task=f"add deps {' '.join(add)}", target=target, workspace=workspace)
        finally:
            os.close(lock_fd)

    args.output.write_text("", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(cli()))
