import unittest
from unittest import mock

import release_publish
from release_constants import BCR_PR_PLACEHOLDER


def make_release(body: str, *, draft: bool = False) -> dict:
    return {"id": 7, "body": body, "draft": draft, "prerelease": True}


class TestMain(unittest.TestCase):
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
        result, update = self.run_main(make_release(f"notes {BCR_PR_PLACEHOLDER}", draft=True))
        self.assertEqual(result, 0)
        update.assert_called_once_with("owner/repo", 7, draft=False, prerelease=True)

    def test_published_release_is_left_alone(self) -> None:
        result, update = self.run_main(make_release("notes", draft=False))
        self.assertEqual(result, 0)
        update.assert_not_called()


if __name__ == "__main__":
    unittest.main()
