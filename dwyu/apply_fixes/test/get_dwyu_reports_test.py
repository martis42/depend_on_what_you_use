import argparse
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from python.runfiles import Runfiles

from dwyu.apply_fixes.get_dwyu_reports import gather_reports, get_reports_search_dir, parse_dwyu_execution_log


class TestGatherReports(unittest.TestCase):
    def test_gather_reports_from_filesystem(self) -> None:
        runfiles = Runfiles.Create()
        search_path = Path(
            runfiles.Rlocation(
                "depend_on_what_you_use/dwyu/apply_fixes/test/data/gather_reports_search_path/root_target_dwyu_report.json"
            )
        ).parent
        args = argparse.Namespace(dwyu_log_file=None)

        reports = gather_reports(args, search_path)

        self.assertEqual(
            sorted(reports),
            sorted(
                [
                    search_path / "root_target_dwyu_report.json",
                    search_path / "sub" / "nested_target_dwyu_report.json",
                ]
            ),
        )

    def test_gather_reports_from_log_file(self) -> None:
        log_file = Path("gather_reports_test_log.txt")
        log_file.write_text("DWYU Report: bazel-out/opt/bin/some/target_dwyu_report.json\n")
        args = argparse.Namespace(dwyu_log_file=log_file)

        reports = gather_reports(args, search_path=Path("/search"))

        self.assertEqual(reports, [Path("/search/some/target_dwyu_report.json")])

    def test_gather_reports_from_log_file_does_not_exist(self) -> None:
        args = argparse.Namespace(dwyu_log_file=Path("no_such_file.txt"))

        with self.assertRaisesRegex(FileNotFoundError, "no_such_file.txt"):
            gather_reports(args, search_path=Path("/search"))

    def test_gather_reports_from_log_file_unexpected_format(self) -> None:
        log_file = Path("gather_reports_test_log_bad.txt")
        log_file.write_text("DWYU Report: no_bin_separator_dwyu_report.json\n")
        args = argparse.Namespace(dwyu_log_file=log_file)

        with self.assertRaisesRegex(RuntimeError, "Unexpected report path format"):
            gather_reports(args, search_path=Path("/search"))


class TestParseDwyuExecutionLog(unittest.TestCase):
    def test_parse_dwyu_execution_log(self) -> None:
        test_log = Path("test_log.txt")
        test_log.write_text(
            """
Some unrelated stuff
DWYU Report: bazel-out/opt/bin/some/target_dwyu_report.json
ERROR: Unrelated error
DWYU Report: bazel-out/opt/bin/root_target_dwyu_report.json
""".strip()
        )

        logs = parse_dwyu_execution_log(test_log)
        self.assertEqual(
            logs, ["bazel-out/opt/bin/some/target_dwyu_report.json", "bazel-out/opt/bin/root_target_dwyu_report.json"]
        )

    def test_parse_dwyu_execution_log_empty(self) -> None:
        test_log = Path("test_log.txt")
        test_log.write_text("")

        logs = parse_dwyu_execution_log(test_log)
        self.assertEqual(logs, [])


class TestGetReportsSearchDir(unittest.TestCase):
    def test_search_path_from_args(self) -> None:
        args = argparse.Namespace(search_path=Path("/explicit/search/path"))

        result = get_reports_search_dir(args, workspace_root=Path("/workspace"))

        self.assertEqual(result, Path("/explicit/search/path"))

    @patch("dwyu.apply_fixes.get_dwyu_reports.execute_and_capture")
    def test_search_dir_via_bazel_info(self, mock_execute: MagicMock) -> None:
        mock_execute.return_value.stdout = "/bazel/output/bin\n"
        args = argparse.Namespace(search_path=None, use_bazel_info=True, bazel_startup_args=None, bazel_args=None)

        result = get_reports_search_dir(args, workspace_root=Path("/workspace"))

        self.assertEqual(result, Path("/bazel/output/bin"))

    @patch.object(Path, "resolve", return_value=Path("/resolved/bazel-bin"))
    @patch.object(Path, "is_dir", return_value=True)
    def test_search_dir_via_convenience_symlink(self, _is_dir: MagicMock, _resolve: MagicMock) -> None:
        args = argparse.Namespace(search_path=None, use_bazel_info=False)

        result = get_reports_search_dir(args, workspace_root=Path("/workspace"))

        self.assertEqual(result, Path("/resolved/bazel-bin"))

    @patch.object(Path, "is_dir", return_value=False)
    def test_missing_convenience_symlink(self, _: MagicMock) -> None:
        args = argparse.Namespace(search_path=None, use_bazel_info=False)

        with self.assertLogs(level="FATAL") as captured_logs, self.assertRaises(SystemExit) as exit_ctx:
            get_reports_search_dir(args, workspace_root=Path("/workspace"))

        self.assertEqual(exit_ctx.exception.code, 1)
        self.assertEqual(len(captured_logs.output), 1)
        self.assertTrue(captured_logs.output[0].startswith("CRITICAL:root:ERROR: convenience symlink"))


if __name__ == "__main__":
    unittest.main()
