import json
import subprocess
import unittest
from unittest import mock

import release_finalize
import release_github
import release_publish
from release_constants import BCR_PR_PLACEHOLDER, BCR_WARNING_END, BCR_WARNING_START, FAILED_CHANGES_MARKER


class TestGhApi(unittest.TestCase):
    def test_payload_is_sent_as_json_via_stdin(self) -> None:
        completed = subprocess.CompletedProcess([], 0, stdout="{}", stderr="")
        with mock.patch("subprocess.run", return_value=completed) as run:
            release_github.update_release("owner/repo", 42, body="{owner} @file", draft=False, make_latest="true")

        cmd = run.call_args.args[0]
        self.assertEqual(cmd[:3], ["gh", "api", "repos/owner/repo/releases/42"])
        self.assertIn("PATCH", cmd)
        self.assertEqual(cmd[-2:], ["--input", "-"])
        self.assertEqual(
            json.loads(run.call_args.kwargs["input"]),
            {"body": "{owner} @file", "draft": False, "make_latest": "true"},
        )

    def test_no_payload_means_no_input_option(self) -> None:
        completed = subprocess.CompletedProcess([], 0, stdout="[]", stderr="")
        with mock.patch("subprocess.run", return_value=completed) as run:
            release_github.gh_api("repos/owner/repo/releases")
        self.assertEqual(run.call_args.args[0], ["gh", "api", "repos/owner/repo/releases"])
        self.assertIsNone(run.call_args.kwargs["input"])

    def test_error_message_of_api_is_logged(self) -> None:
        error = subprocess.CalledProcessError(1, ["gh"], output='{"message": "Validation Failed"}', stderr="HTTP 422")
        with (
            mock.patch("subprocess.run", side_effect=error),
            self.assertLogs(release_github.log, level="ERROR") as logs,
            self.assertRaises(subprocess.CalledProcessError),
        ):
            release_github.gh_api("repos/owner/repo/releases/1")
        self.assertIn("Validation Failed", logs.output[0])
        self.assertIn("HTTP 422", logs.output[0])


def make_release(body: str, *, draft: bool = False, prerelease: bool = True) -> dict:
    return {"id": 7, "body": body, "draft": draft, "prerelease": prerelease}


class TestFinalizeMain(unittest.TestCase):
    BODY = f"## Using\n\n{BCR_WARNING_START}\nwarning\n{BCR_WARNING_END}\n\nrest"

    def run_main(self, release: dict, *, merged: bool = True, newest: bool | Exception = True) -> tuple[int, mock.Mock]:
        bcr_pr = {"html_url": "https://example.com/pr", "merged_at": "2026-01-01" if merged else None}
        with (
            mock.patch("sys.argv", ["release_finalize.py", "--tag", "1.2.3", "--repo", "owner/repo"]),
            mock.patch.object(release_finalize, "find_release", return_value=release),
            mock.patch.object(release_finalize, "find_bcr_pr", return_value=bcr_pr),
            mock.patch.object(release_finalize, "is_newest_release", side_effect=[newest]),
            mock.patch.object(release_finalize, "update_release") as update,
            self.assertLogs(release_finalize.log, level="INFO"),
        ):
            return release_finalize.main(), update

    def test_finalizes_newest_release(self) -> None:
        result, update = self.run_main(make_release(self.BODY))
        self.assertEqual(result, 0)
        update.assert_called_once_with("owner/repo", 7, body="## Using\n\nrest", prerelease=False, make_latest="true")

    def test_patch_for_old_release_is_not_latest(self) -> None:
        _, update = self.run_main(make_release(self.BODY), newest=False)
        self.assertEqual(update.call_args.kwargs["make_latest"], "false")

    def test_undeterminable_latest_status_aborts(self) -> None:
        result, update = self.run_main(make_release(self.BODY), newest=RuntimeError("no tags"))
        self.assertEqual(result, 1)
        update.assert_not_called()

    def test_failed_changes_marker_aborts(self) -> None:
        result, update = self.run_main(make_release(f"{FAILED_CHANGES_MARKER}\n{self.BODY}"))
        self.assertEqual(result, 1)
        update.assert_not_called()

    def test_unmerged_bcr_pr_aborts(self) -> None:
        result, update = self.run_main(make_release(self.BODY), merged=False)
        self.assertEqual(result, 1)
        update.assert_not_called()

    def test_draft_aborts(self) -> None:
        result, update = self.run_main(make_release(self.BODY, draft=True))
        self.assertEqual(result, 1)
        update.assert_not_called()

    def test_already_finalized_does_nothing(self) -> None:
        result, update = self.run_main(make_release(self.BODY, prerelease=False))
        self.assertEqual(result, 0)
        update.assert_not_called()


class TestPublishMain(unittest.TestCase):
    def run_main(self, release: dict) -> tuple[int, mock.Mock]:
        with (
            mock.patch("sys.argv", ["release_publish.py", "--tag", "1.2.3", "--repo", "owner/repo"]),
            mock.patch.object(release_publish, "find_release", return_value=release),
            mock.patch.object(release_publish, "update_release") as update,
            self.assertLogs(release_publish.log, level="INFO"),
        ):
            return release_publish.main(), update

    def test_publishes_draft_as_prerelease(self) -> None:
        result, update = self.run_main(make_release("notes", draft=True))
        self.assertEqual(result, 0)
        update.assert_called_once_with("owner/repo", 7, draft=False, prerelease=True)

    def test_problematic_release_notes_only_cause_warnings(self) -> None:
        for text in (BCR_PR_PLACEHOLDER, FAILED_CHANGES_MARKER):
            with self.subTest(text=text):
                result, update = self.run_main(make_release(f"notes {text}", draft=True))
                self.assertEqual(result, 0)
                update.assert_called_once_with("owner/repo", 7, draft=False, prerelease=True)

    def test_published_release_is_left_alone(self) -> None:
        result, update = self.run_main(make_release("notes", draft=False))
        self.assertEqual(result, 0)
        update.assert_not_called()


if __name__ == "__main__":
    unittest.main()
