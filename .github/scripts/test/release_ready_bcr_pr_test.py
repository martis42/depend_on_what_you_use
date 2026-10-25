import unittest
from unittest import mock

import release_ready_bcr_pr


def make_pr(*, state: str = "open", draft: bool = True, merged_at: str | None = None) -> dict:
    return {"html_url": "https://example.com/pr/1", "state": state, "draft": draft, "merged_at": merged_at}


class TestMain(unittest.TestCase):
    def run_main(self, pr: dict) -> tuple[int, mock.Mock]:
        with (
            mock.patch("sys.argv", ["release_ready_bcr_pr.py", "--tag", "1.2.3"]),
            mock.patch.object(release_ready_bcr_pr, "find_bcr_pr", return_value=pr),
            mock.patch.object(release_ready_bcr_pr.subprocess, "run") as run,
            self.assertLogs(release_ready_bcr_pr.log, level="INFO"),
        ):
            return release_ready_bcr_pr.main(), run

    def test_draft_pr_is_marked_ready(self) -> None:
        result, run = self.run_main(make_pr())
        self.assertEqual(result, 0)
        run.assert_called_once_with(["gh", "pr", "ready", "https://example.com/pr/1"], check=True)

    def test_pr_already_ready_is_left_alone(self) -> None:
        result, run = self.run_main(make_pr(draft=False))
        self.assertEqual(result, 0)
        run.assert_not_called()

    def test_merged_pr_is_left_alone(self) -> None:
        result, run = self.run_main(make_pr(state="closed", draft=False, merged_at="2026-01-01T00:00:00Z"))
        self.assertEqual(result, 0)
        run.assert_not_called()

    def test_pr_closed_without_merge_fails(self) -> None:
        for draft in (True, False):
            with self.subTest(draft=draft):
                result, run = self.run_main(make_pr(state="closed", draft=draft))
                self.assertEqual(result, 1)
                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
