import subprocess
import unittest
from collections.abc import Callable
from unittest import mock

import release_finalize
import release_prep
from release_constants import BCR_WARNING_END, BCR_WARNING_START
from release_finalize import is_newest_release, remove_bcr_warning


class TestRemoveBcrWarning(unittest.TestCase):
    def test_removes_warning_from_generated_release_notes(self) -> None:
        notes = release_prep.RELEASE_NOTES_TEMPLATE.format(
            CHANGES="## Noteworthy Changes\n\n- Something",
            BCR_WARNING_START=BCR_WARNING_START,
            BCR_WARNING_END=BCR_WARNING_END,
            BCR_PR="https://example.com/pr/1",
            VERSION="1.2.3",
        )
        expected = """## Noteworthy Changes

- Something

## Using this release

Add to your `MODULE.bazel` file:

```starlark
bazel_dep(name = "depend_on_what_you_use", version = "1.2.3")
```

---"""
        self.assertEqual(remove_bcr_warning(notes), expected)

    def test_only_content_between_markers_is_removed(self) -> None:
        body = f"before\n\n{BCR_WARNING_START}\nwarning\nmore warning\n{BCR_WARNING_END}\n\nafter"
        self.assertEqual(remove_bcr_warning(body), "before\n\nafter")

    def test_missing_markers_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            remove_bcr_warning("## Using this release\n\nSomething else")

    def test_missing_end_marker_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            remove_bcr_warning(f"before\n{BCR_WARNING_START}\nwarning\nafter")

    def test_wrong_marker_order_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            remove_bcr_warning(f"{BCR_WARNING_END}\nwarning\n{BCR_WARNING_START}")

    def test_duplicated_markers_are_rejected(self) -> None:
        body = f"{BCR_WARNING_START}\na\n{BCR_WARNING_END}\n{BCR_WARNING_START}\nb\n{BCR_WARNING_END}"
        with self.assertRaises(ValueError):
            remove_bcr_warning(body)


def fake_git_subprocess(tags: str, fetch_returncode: int = 0) -> Callable[..., subprocess.CompletedProcess]:
    def run(cmd: list[str], **_: object) -> subprocess.CompletedProcess:
        if cmd[:2] == ["git", "fetch"]:
            return subprocess.CompletedProcess(cmd, fetch_returncode, stdout="", stderr="no network")
        return subprocess.CompletedProcess(cmd, 0, stdout=tags, stderr="")

    return run


class TestIsNewestRelease(unittest.TestCase):
    def is_newest(self, tag: str, tags: str, fetch_returncode: int = 0) -> bool:
        with mock.patch(
            "subprocess.run", side_effect=fake_git_subprocess(tags=tags, fetch_returncode=fetch_returncode)
        ):
            return is_newest_release(tag)

    def test_highest_tag(self) -> None:
        self.assertTrue(self.is_newest("1.2.0", "1.0.0\n1.1.0\n1.1.1\n1.2.0\n"))

    def test_only_tag(self) -> None:
        self.assertTrue(self.is_newest("1.0.0", "1.0.0\n"))

    def test_patch_for_old_release(self) -> None:
        self.assertFalse(self.is_newest("1.1.1", "1.1.0\n1.1.1\n1.2.0\n"))

    def test_numeric_not_lexicographic_comparison(self) -> None:
        self.assertTrue(self.is_newest("1.10.0", "1.9.0\n1.10.0\n"))
        self.assertFalse(self.is_newest("1.9.1", "1.9.1\n1.10.0\n"))

    def test_unrelated_tags_are_ignored(self) -> None:
        self.assertTrue(self.is_newest("1.0.1", "1.0.0\n1.0.1\nsome-tag\n9.9.9-rc1\n"))

    def test_tag_missing_locally_warns(self) -> None:
        with self.assertLogs("release_finalize", level="WARNING"):
            self.assertFalse(self.is_newest("1.2.0", "1.1.0\n"))

    def test_invalid_tag_format_warns(self) -> None:
        with self.assertLogs("release_finalize", level="WARNING"):
            self.assertFalse(self.is_newest("v1.2.0", "v1.2.0\n"))

    def test_fetch_failure_warns(self) -> None:
        with self.assertLogs("release_finalize", level="WARNING"):
            self.assertFalse(self.is_newest("1.2.0", "1.1.0\n1.2.0\n", fetch_returncode=1))


def make_release(body: str, *, draft: bool = False, prerelease: bool = True) -> dict:
    return {"id": 7, "body": body, "draft": draft, "prerelease": prerelease}


class TestMain(unittest.TestCase):
    BODY = f"## Using\n\n{BCR_WARNING_START}\nwarning\n{BCR_WARNING_END}\n\nrest"

    def run_main(self, release: dict, *, merged: bool = True, newest: bool = True) -> tuple[int, mock.Mock]:
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


if __name__ == "__main__":
    unittest.main()
