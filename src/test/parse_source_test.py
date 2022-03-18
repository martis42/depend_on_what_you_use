import unittest
from pathlib import Path

from src.parse_source import (Include, filter_includes, get_includes_from_file,
                              get_relevant_includes_from_files)


class TestInclude(unittest.TestCase):
    def test_in(self):
        unit = [Include(file=Path("foo"), include="foo.h"), Include(file=Path("bar"), include="bar.h")]

        self.assertTrue(Include(file=Path("foo"), include="foo.h") in unit)
        self.assertTrue(Include(file=Path("bar"), include="bar.h") in unit)

    def test_hash(self):
        foo = Include(file=Path("foo"), include="bar")
        unit = {foo, foo, Include(file=Path("foo"), include="bar"), Include(file=Path("bar"), include="foo")}

        self.assertEqual(len(unit), 2)
        self.assertTrue(Include(file=Path("foo"), include="bar") in unit)
        self.assertTrue(Include(file=Path("bar"), include="foo") in unit)

    def test_str(self):
        unit = Include(file=Path("foo"), include="bar")

        self.assertEqual(str(unit), "File='foo', include='bar'")


class TestFilterIncludes(unittest.TestCase):
    def test_filter_includes(self):
        result = filter_includes(
            includes=[
                Include(file=Path("file1"), include="hiho.h"),
                Include(file=Path("file2"), include="foo"),
                Include(file=Path("file3"), include="some/deep/path.h"),
                Include(file=Path("file4"), include="bar/baz.h"),
            ],
            ignored_includes={"foo", "bar/baz.h"},
        )

        self.assertEqual(len(result), 2)
        self.assertTrue(Include(file=Path("file1"), include="hiho.h") in result)
        self.assertTrue(Include(file=Path("file3"), include="some/deep/path.h") in result)


class TestGetIncludesFromFile(unittest.TestCase):
    def test_single_include(self):
        test_file = Path("src/test/data/another_header.h")
        result = get_includes_from_file(test_file)

        self.assertEqual(result, [Include(file=test_file, include="foo/bar.h")])

    def test_multiple_includes(self):
        test_file = Path("src/test/data/some_header.h")
        result = get_includes_from_file(test_file)

        self.assertEqual(len(result), 4)
        self.assertTrue(Include(file=test_file, include="bar.h") in result)
        self.assertTrue(Include(file=test_file, include="foo/bar/baz.h") in result)
        self.assertTrue(Include(file=test_file, include="some/path/to_a/system_header.h") in result)

    def test_commented_includes_single_line_comments(self):
        test_file = Path("src/test/data/commented_includes/single_line_comments.h")
        result = get_includes_from_file(test_file)

        self.assertEqual(result, [Include(file=test_file, include="active.h")])

    def test_commented_includes_block_comments(self):
        test_file = Path("src/test/data/commented_includes/block_comments.h")
        result = get_includes_from_file(test_file)

        self.assertEqual(len(result), 5)
        self.assertTrue(Include(file=test_file, include="active_a.h") in result)
        self.assertTrue(Include(file=test_file, include="active_b.h") in result)
        self.assertTrue(Include(file=test_file, include="active_c.h") in result)
        self.assertTrue(Include(file=test_file, include="active_d.h") in result)
        self.assertTrue(Include(file=test_file, include="active_e.h") in result)

    def test_commented_includes_mixed_style(self):
        test_file = Path("src/test/data/commented_includes/mixed_style.h")
        result = get_includes_from_file(test_file)

        self.assertEqual(result, [Include(file=test_file, include="active.h")])


class TestGetRelevantIncludesFromFiles(unittest.TestCase):
    def test_get_relevant_includes_from_files(self):
        result = get_relevant_includes_from_files(
            files=["src/test/data/some_header.h", "src/test/data/another_header.h"], ignored_includes={"vector"}
        )

        self.assertEqual(len(result), 4)
        self.assertTrue(Include(file=Path("src/test/data/some_header.h"), include="bar.h") in result)
        self.assertTrue(Include(file=Path("src/test/data/some_header.h"), include="foo/bar/baz.h") in result)
        self.assertTrue(
            Include(file=Path("src/test/data/some_header.h"), include="some/path/to_a/system_header.h") in result
        )
        self.assertTrue(Include(file=Path("src/test/data/another_header.h"), include="foo/bar.h") in result)


if __name__ == "__main__":
    unittest.main()
