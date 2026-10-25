import subprocess
import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from unittest import mock

import release_prep

CHANGELOG_CONTENT = """# Changelog

## Unreleased

### Fixed

- Something

## [1.0.0](https://example.com) - 2026.01.01

### Added

- Old thing
"""


def fake_git_subprocess(tags: str, fetch_returncode: int = 0) -> Callable[..., subprocess.CompletedProcess]:
    def run(cmd: list[str], **_: object) -> subprocess.CompletedProcess:
        if cmd[:2] == ["git", "fetch"]:
            return subprocess.CompletedProcess(cmd, fetch_returncode, stdout="", stderr="no network")
        return subprocess.CompletedProcess(cmd, 0, stdout=tags, stderr="")

    return run


class TestExtractUnreleasedChangelog(unittest.TestCase):
    def extract(self, content: str) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            changelog = Path(tmp) / "CHANGELOG.md"
            changelog.write_text(content, encoding="utf-8")
            return release_prep.extract_unreleased_changelog(changelog)

    def test_content_until_first_old_release(self) -> None:
        self.assertEqual(self.extract(CHANGELOG_CONTENT), "### Fixed\n\n- Something")

    def test_empty_unreleased_section(self) -> None:
        self.assertEqual(self.extract("## Unreleased\n\n## [1.0.0](x) - date\n\n- Old\n"), "")

    def test_unreleased_section_is_last(self) -> None:
        self.assertEqual(self.extract("## Unreleased\n\n- New\n"), "- New")

    def test_no_unreleased_section(self) -> None:
        self.assertEqual(self.extract("## [1.0.0](x) - date\n\n- Old\n"), "")


class TestIsNewestRelease(unittest.TestCase):
    def is_newest(self, tag: str, tags: str, fetch_returncode: int = 0) -> bool:
        with mock.patch(
            "subprocess.run", side_effect=fake_git_subprocess(tags=tags, fetch_returncode=fetch_returncode)
        ):
            return release_prep.is_newest_release(tag)

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

    def test_tag_missing_locally(self) -> None:
        self.assertFalse(self.is_newest("1.2.0", "1.1.0\n"))

    def test_invalid_tag_format(self) -> None:
        self.assertFalse(self.is_newest("v1.2.0", "v1.2.0\n"))

    def test_fetch_failure(self) -> None:
        self.assertFalse(self.is_newest("1.2.0", "1.1.0\n1.2.0\n", fetch_returncode=1))


NOTES_FOOTER = """## Using this release

:construction: **Deployment to BCR is not yet finished.** The release will be usable via bzlmod after this PR merged: BCR_PR_URL_PLACEHOLDER

Add to your `MODULE.bazel` file:

```starlark
bazel_dep(name = "depend_on_what_you_use", version = "{version}")
```

---"""


class TestCreateReleaseNotes(unittest.TestCase):
    def create_notes(self, tag: str, changelog_content: str, existing_tags: str) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            changelog = Path(tmp) / "CHANGELOG.md"
            changelog.write_text(changelog_content, encoding="utf-8")
            with mock.patch("subprocess.run", side_effect=fake_git_subprocess(existing_tags)):
                return release_prep.create_release_notes(tag=tag, changelog=changelog)

    def test_newest_release_with_unreleased_changes(self) -> None:
        expected = """## Noteworthy Changes

### Fixed

- Something

""" + NOTES_FOOTER.format(version="1.1.0")
        self.assertEqual(self.create_notes("1.1.0", CHANGELOG_CONTENT, "1.0.0\n1.1.0\n"), expected)

    def test_newest_release_without_unreleased_changes(self) -> None:
        changelog = "## Unreleased\n\n## [1.0.0](x) - date\n\n- Old\n"
        expected = NOTES_FOOTER.format(version="1.1.0")
        self.assertEqual(self.create_notes("1.1.0", changelog, "1.0.0\n1.1.0\n"), expected)

    def test_patch_for_old_release_does_not_copy_changes(self) -> None:
        expected = """## Noteworthy Changes

FAILED_TO_AUTOMATICALLY_ADD_RELEASED_CHANGES

""" + NOTES_FOOTER.format(version="1.0.1")
        self.assertEqual(self.create_notes("1.0.1", CHANGELOG_CONTENT, "1.0.0\n1.0.1\n1.1.0\n"), expected)


if __name__ == "__main__":
    unittest.main()
