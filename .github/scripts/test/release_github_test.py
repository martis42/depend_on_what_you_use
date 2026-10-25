import json
import subprocess
import unittest
from unittest import mock

import release_github


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


if __name__ == "__main__":
    unittest.main()
