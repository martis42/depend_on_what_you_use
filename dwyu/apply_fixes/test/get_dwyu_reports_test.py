import unittest
from pathlib import Path

from dwyu.apply_fixes.get_dwyu_reports import parse_dwyu_execution_log


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


if __name__ == "__main__":
    unittest.main()
