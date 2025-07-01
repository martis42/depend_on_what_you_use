from __future__ import annotations

import logging
import platform
import sys
from os import walk
from pathlib import Path
from typing import TYPE_CHECKING

from src.apply_fixes.utils import args_string_to_list, execute_and_capture

if TYPE_CHECKING:
    import argparse


def gather_reports(main_args: argparse.Namespace, search_path: Path) -> list[Path]:
    if main_args.dwyu_log_file:
        bin_dir = "\\bin\\" if platform.system() == "Windows" else "/bin/"
        return [search_path / log.split(bin_dir, 1)[1] for log in parse_dwyu_execution_log(main_args.dwyu_log_file)]

    reports = []
    # We explicitly use os.walk() as it has better performance than Path.glob() in large and deeply nested file trees.
    for root, _, files in walk(search_path):
        for file in files:
            if file.endswith("_dwyu_report.json"):
                reports.append(Path(root) / file)  # noqa: PERF401
    return reports


def parse_dwyu_execution_log(log_file: Path) -> list[str]:
    dwyu_report_anchor = "DWYU Report: "
    with log_file.open() as log:
        return [
            line.strip().split(dwyu_report_anchor)[1] for line in log.readlines() if line.startswith(dwyu_report_anchor)
        ]


def get_reports_search_dir(main_args: argparse.Namespace, workspace_root: Path) -> Path:
    """
    Unless an alternative method is selected, follow the convenience symlinks at the workspace root to discover the
    DWYU report files.
    """
    if main_args.search_path:
        return Path(main_args.search_path)

    if main_args.use_bazel_info:
        process = execute_and_capture(
            cmd=[
                "bazel",
                *args_string_to_list(main_args.bazel_startup_args),
                "info",
                *args_string_to_list(main_args.bazel_args),
                "bazel-bin",
            ],
            cwd=workspace_root,
        )
        return Path(process.stdout.strip())

    bazel_bin_link = workspace_root / "bazel-bin"
    if not bazel_bin_link.is_dir():
        logging.fatal(f"ERROR: convenience symlink '{bazel_bin_link}' does not exist.")
        sys.exit(1)
    return bazel_bin_link.resolve()
