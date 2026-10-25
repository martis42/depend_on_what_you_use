import tempfile
import unittest
from pathlib import Path

import release_prep

CHANGELOG_CONTENT = """# Changelog

## Unreleased

- Not yet released

## [1.1.0](https://example.com) - 2026.02.01

### Fixed

- Something

## [1.0.1](https://example.com) - 2026.01.15

### Changed

- Patch

## [1.0.0](https://example.com) - 2026.01.01

### Added

- Old thing
"""


class TestExtractReleaseChangelog(unittest.TestCase):
    def extract(self, tag: str, content: str) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            changelog = Path(tmp) / "CHANGELOG.md"
            changelog.write_text(content, encoding="utf-8")
            return release_prep.extract_release_changelog(tag, changelog)

    def test_content_until_next_release_headline(self) -> None:
        self.assertEqual(self.extract("1.1.0", CHANGELOG_CONTENT), "### Fixed\n\n- Something")

    def test_release_in_between_other_releases(self) -> None:
        self.assertEqual(self.extract("1.0.1", CHANGELOG_CONTENT), "### Changed\n\n- Patch")

    def test_release_is_last_section(self) -> None:
        self.assertEqual(self.extract("1.0.0", CHANGELOG_CONTENT), "### Added\n\n- Old thing")

    def test_empty_release_section(self) -> None:
        self.assertEqual(self.extract("1.1.0", "## [1.1.0](x) - date\n\n## [1.0.0](x) - date\n\n- Old\n"), "")

    def test_version_not_in_changelog(self) -> None:
        self.assertEqual(self.extract("2.0.0", CHANGELOG_CONTENT), "")

    def test_unreleased_section_is_ignored(self) -> None:
        self.assertEqual(self.extract("1.1.0", "## Unreleased\n\n- New\n"), "")

    def test_version_must_match_completely(self) -> None:
        self.assertEqual(self.extract("1.1", CHANGELOG_CONTENT), "")
        self.assertEqual(self.extract("1.1.0", "## [1.1.01](x) - date\n\n- Other\n"), "")


NOTES_FOOTER = """## Using this release

<!-- BCR_WARNING_START -->
:construction: **Deployment to BCR is not yet finished.** The release will be usable via bzlmod after this PR merged: BCR_PR_URL_PLACEHOLDER
<!-- BCR_WARNING_END -->

Add to your `MODULE.bazel` file:

```starlark
bazel_dep(name = "depend_on_what_you_use", version = "{version}")
```

---"""


class TestCreateReleaseNotes(unittest.TestCase):
    def create_notes(self, tag: str, changelog_content: str) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            changelog = Path(tmp) / "CHANGELOG.md"
            changelog.write_text(changelog_content, encoding="utf-8")
            return release_prep.create_release_notes(tag=tag, changelog=changelog)

    def test_release_with_changelog_section(self) -> None:
        expected = """## Noteworthy Changes

### Fixed

- Something

""" + NOTES_FOOTER.format(version="1.1.0")
        self.assertEqual(self.create_notes("1.1.0", CHANGELOG_CONTENT), expected)

    def test_patch_for_old_release(self) -> None:
        expected = """## Noteworthy Changes

### Changed

- Patch

""" + NOTES_FOOTER.format(version="1.0.1")
        self.assertEqual(self.create_notes("1.0.1", CHANGELOG_CONTENT), expected)

    def test_release_with_empty_changelog_section(self) -> None:
        changelog = "## [1.1.0](x) - date\n\n## [1.0.0](x) - date\n\n- Old\n"
        self.assertEqual(self.create_notes("1.1.0", changelog), NOTES_FOOTER.format(version="1.1.0"))

    def test_release_without_changelog_section(self) -> None:
        self.assertEqual(self.create_notes("2.0.0", CHANGELOG_CONTENT), NOTES_FOOTER.format(version="2.0.0"))


if __name__ == "__main__":
    unittest.main()
