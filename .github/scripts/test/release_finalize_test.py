import unittest

import release_prep
from release_constants import BCR_WARNING_END, BCR_WARNING_START
from release_finalize import remove_bcr_warning


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


if __name__ == "__main__":
    unittest.main()
