import json
import unittest
from unittest import mock

import release_add_bcr_pr
import release_github
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
        update.assert_called_once_with(
            "owner/repo", make_release("notes", draft=True), "1.2.3", draft=False, prerelease=True
        )

    def test_problematic_release_notes_only_cause_warnings(self) -> None:
        result, update = self.run_main(make_release(f"notes {BCR_PR_PLACEHOLDER}", draft=True))
        self.assertEqual(result, 0)
        update.assert_called_once_with(
            "owner/repo", make_release(f"notes {BCR_PR_PLACEHOLDER}", draft=True), "1.2.3", draft=False, prerelease=True
        )

    def test_published_release_is_left_alone(self) -> None:
        result, update = self.run_main(make_release("notes", draft=False))
        self.assertEqual(result, 0)
        update.assert_not_called()


class TestDraftReleaseSequence(unittest.TestCase):
    def test_editing_notes_then_publishing_preserves_tag(self) -> None:
        release = {
            "id": 7,
            "tag_name": "1.2.3",
            "body": f"notes {BCR_PR_PLACEHOLDER}",
            "draft": True,
            "prerelease": True,
        }
        pr_url = "https://example.com/pr/1"

        def gh_api(endpoint: str, *args: str, payload: dict | None = None) -> str:
            if endpoint.startswith("repos/bazelbuild/bazel-central-registry/pulls?"):
                return json.dumps([{"html_url": pr_url}])
            if endpoint.startswith("repos/owner/repo/releases?"):
                return json.dumps([release])
            self.assertEqual(endpoint, "repos/owner/repo/releases/7")
            self.assertEqual(args, ("--method", "PATCH"))
            if payload is None:
                self.fail("PATCH must include a payload")
            if release["draft"] and "tag_name" not in payload:
                release["tag_name"] = "untagged-generated"
            release.update(payload)
            return json.dumps(release)

        with (
            mock.patch.object(release_github, "gh_api", side_effect=gh_api),
            mock.patch("sys.argv", ["script", "--tag", "1.2.3", "--repo", "owner/repo"]),
        ):
            self.assertEqual(release_add_bcr_pr.main(), 0)
            self.assertEqual(release["tag_name"], "1.2.3")
            self.assertEqual(release["body"], f"notes {pr_url}")
            self.assertEqual(release_publish.main(), 0)
            self.assertEqual(release["tag_name"], "1.2.3")
            self.assertFalse(release["draft"])
            self.assertTrue(release["prerelease"])


if __name__ == "__main__":
    unittest.main()
