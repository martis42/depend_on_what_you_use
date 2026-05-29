import argparse
from os import walk
from pathlib import Path

from dwyu.apply_fixes.utils import args_string_to_list, execute_and_capture


def gather_reports(main_args: argparse.Namespace, search_path: Path) -> list[Path]:
    reports = []

    if main_args.dwyu_log_file:
        if not main_args.dwyu_log_file.is_file():
            raise FileNotFoundError(f"ERROR: The provided DWYU log file '{main_args.dwyu_log_file}' does not exist.")
        for report in parse_dwyu_execution_log(main_args.dwyu_log_file):
            if "/bin/" in report:
                reports.append(search_path / report.split("/bin/", 1)[1])
            else:
                raise RuntimeError(f"Unexpected report path format: '{report}'")
        return reports

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
    if main_args.reports_search_path:
        if not main_args.reports_search_path.is_dir():
            raise FileNotFoundError(
                f"ERROR: The provided search path '{main_args.reports_search_path}' does not exist."
            )
        return main_args.reports_search_path

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
