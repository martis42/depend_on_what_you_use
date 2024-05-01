from __future__ import annotations

import json
import logging
import shlex
import sys
from os import environ, walk
from pathlib import Path
from typing import TYPE_CHECKING

from src.apply_fixes.bazel_query import BazelQuery
from src.apply_fixes.buildozer_executor import BuildozerExecutor
from src.apply_fixes.search_missing_deps import search_missing_deps
from src.apply_fixes.utils import execute_and_capture

if TYPE_CHECKING:
    from argparse import Namespace

logging.basicConfig(format="%(message)s", level=logging.INFO)

# Bazel sets this environment for 'bazel run' to document the workspace root
WORKSPACE_ENV_VAR = "BUILD_WORKSPACE_DIRECTORY"


class RequestedFixes:
    def __init__(self, main_args: Namespace) -> None:
        self.remove_unused_deps = main_args.fix_unused_deps or main_args.fix_all
        self.move_private_deps_to_impl_deps = main_args.fix_deps_which_should_be_private or main_args.fix_all
        self.add_missing_deps = main_args.fix_missing_deps or main_args.fix_all


def get_workspace(main_args: Namespace) -> Path | None:
    if main_args.workspace:
        return Path(main_args.workspace)

    workspace_root = environ.get(WORKSPACE_ENV_VAR)
    if not workspace_root:
        return None
    return Path(workspace_root)


def get_reports_search_dir(main_args: Namespace, workspace_root: Path) -> Path:
    """
    Unless a dedicated search directory is provided, try to deduce the 'bazel-bin' dir.
    """
    if main_args.search_path:
        return Path(main_args.search_path)

    if main_args.use_bazel_info:
        process = execute_and_capture(
            cmd=["bazel", "info", f"--compilation_mode={main_args.use_bazel_info}", "bazel-bin"], cwd=workspace_root
        )
        return Path(process.stdout.strip())

    bazel_bin_link = workspace_root / "bazel-bin"
    if not bazel_bin_link.is_dir():
        logging.fatal(f"ERROR: convenience symlink '{bazel_bin_link}' does not exist or is not a symlink.")
        sys.exit(1)
    return bazel_bin_link.resolve()


def gather_reports(search_path: Path) -> list[Path]:
    """
    We explicitly use os.walk() as it has better performance than Path.glob() in large and deeply nested file trees.
    """
    reports = []
    for root, _, files in walk(search_path):
        for file in files:
            if file.endswith("_dwyu_report.json"):
                reports.append(Path(root) / file)  # noqa: PERF401
    return reports


def add_discovered_deps(
    discovered_public_deps: list[str],
    discovered_private_deps: list[str],
    target: str,
    buildozer: BuildozerExecutor,
    use_impl_deps: bool,
) -> None:
    add_to_deps = discovered_public_deps
    add_to_impl_deps = []
    if use_impl_deps:
        add_to_impl_deps = [dep for dep in discovered_private_deps if dep not in add_to_deps]
    else:
        add_to_deps.extend(discovered_private_deps)

    if add_to_deps:
        buildozer.execute(task=f"add deps {' '.join(list(set(add_to_deps)))}", target=target)
    if add_to_impl_deps:
        buildozer.execute(task=f"add implementation_deps {' '.join(list(set(add_to_impl_deps)))}", target=target)


def perform_fixes(
    bazel_query: BazelQuery, buildozer: BuildozerExecutor, report: Path, requested_fixes: RequestedFixes
) -> None:
    with report.open(encoding="utf-8") as report_in:
        content = json.load(report_in)
        target = content["analyzed_target"]

        if requested_fixes.remove_unused_deps:
            if unused_deps := content["unused_deps"]:
                buildozer.execute(task=f"remove deps {' '.join(unused_deps)}", target=target)
            if unused_deps := content["unused_implementation_deps"]:
                buildozer.execute(task=f"remove implementation_deps {' '.join(unused_deps)}", target=target)

        if requested_fixes.move_private_deps_to_impl_deps:
            deps_which_should_be_private = content["deps_which_should_be_private"]
            if deps_which_should_be_private:
                buildozer.execute(
                    task=f"move deps implementation_deps {' '.join(deps_which_should_be_private)}", target=target
                )

        if requested_fixes.add_missing_deps:
            discovered_public_deps = search_missing_deps(
                bazel_query=bazel_query,
                target=target,
                includes_without_direct_dep=content["public_includes_without_dep"],
            )
            discovered_private_deps = search_missing_deps(
                bazel_query=bazel_query,
                target=target,
                includes_without_direct_dep=content["private_includes_without_dep"],
            )
            add_discovered_deps(
                discovered_public_deps=discovered_public_deps,
                discovered_private_deps=discovered_private_deps,
                target=target,
                buildozer=buildozer,
                use_impl_deps=content["use_implementation_deps"],
            )


def main(args: Namespace) -> int:
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    buildozer = args.buildozer if args.buildozer else "buildozer"

    workspace = get_workspace(args)
    if not workspace:
        logging.fatal(
            "ERROR: "
            f"No workspace was explicitly provided and environment variable '{WORKSPACE_ENV_VAR}' is not available."
        )
        return 1
    logging.debug(f"Workspace: '{workspace}'")

    reports_search_dir = get_reports_search_dir(main_args=args, workspace_root=workspace)
    logging.debug(f"Reports search directory: '{reports_search_dir}'")

    reports = gather_reports(reports_search_dir)
    if not reports:
        logging.fatal(
            """
ERROR: Did not find any DWYU report files.
Did you forget to run DWYU beforehand?
Maybe the tool used the wrong output directory, have a look at the apply_fixes CLI options via '--help'.
        """.strip()
        )
        return 1

    bazel_query = BazelQuery(
        workspace=workspace,
        use_cquery=args.use_cquery,
        query_args=shlex.split(args.bazel_args) if args.bazel_args else [],
        startup_args=shlex.split(args.bazel_startup_args) if args.bazel_startup_args else [],
    )
    buildozer_executor = BuildozerExecutor(
        buildozer=buildozer, buildozer_args=args.buildozer_args, workspace=workspace, dry=args.dry_run
    )
    for report in reports:
        logging.debug(f"Processing report file '{report}'")
        perform_fixes(
            report=report, bazel_query=bazel_query, buildozer=buildozer_executor, requested_fixes=RequestedFixes(args)
        )
    buildozer_executor.summary.print_summary()

    return 0
