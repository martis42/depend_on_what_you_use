import unittest
from pathlib import Path

from src.analyze_includes.parse_source import (
    IgnoredIncludes,
    Include,
    filter_includes,
    get_includes_from_file,
    get_relevant_includes_from_files,
)


class TestInclude(unittest.TestCase):
    def test_equality(self):
        unit_a = Include(file=Path("foo"), include="foo.h")
        unit_b = Include(file=Path("foo"), include="foo.h")
        unit_c = Include(file=Path("bar"), include="foo.h")
        unit_d = Include(file=Path("foo"), include="bar.h")

        self.assertEqual(unit_a, unit_b)
        self.assertNotEqual(unit_a, unit_c)
        self.assertNotEqual(unit_a, unit_d)
        self.assertNotEqual(unit_c, unit_d)

    def test_in(self):
        unit = [Include(file=Path("foo"), include="foo.h"), Include(file=Path("bar"), include="bar.h")]

        self.assertTrue(Include(file=Path("foo"), include="foo.h") in unit)
        self.assertTrue(Include(file=Path("bar"), include="bar.h") in unit)

    def test_hash(self):
        include = Include(file=Path("foo"), include="bar")
        unit = {include, include, Include(file=Path("foo"), include="bar"), Include(file=Path("bar"), include="foo")}

        self.assertEqual(len(unit), 2)
        self.assertTrue(Include(file=Path("foo"), include="bar") in unit)
        self.assertTrue(Include(file=Path("bar"), include="foo") in unit)

    def test_repr(self):
        unit = Include(file=Path("foo"), include="bar")
        self.assertEqual(repr(unit), "Include(file='foo', include='bar')")

    def test_str(self):
        unit = Include(file=Path("foo"), include="bar")

        self.assertEqual(str(unit), "File='foo', include='bar'")


class TestFilterIncludes(unittest.TestCase):
    def test_filter_includes_for_file_paths(self):
        result = filter_includes(
            includes=[
                Include(file=Path("file1"), include="hiho.h"),
                Include(file=Path("file2"), include="foo"),
                Include(file=Path("file3"), include="foo_pattern_not_match"),
                Include(file=Path("file4"), include="some/other/baz.h"),
                Include(file=Path("file5"), include="bar/baz.h"),
            ],
            ignored_includes=IgnoredIncludes(paths=["foo", "bar/baz.h"], patterns=[]),
        )

        self.assertEqual(len(result), 3)
        self.assertTrue(Include(file=Path("file1"), include="hiho.h") in result)
        self.assertTrue(Include(file=Path("file3"), include="foo_pattern_not_match") in result)
        self.assertTrue(Include(file=Path("file4"), include="some/other/baz.h") in result)

    def test_filter_includes_for_patterns(self):
        result = filter_includes(
            includes=[
                Include(file=Path("file1"), include="some_header.h"),
                Include(file=Path("file2"), include="foo.h"),
                Include(file=Path("file3"), include="foo/bar.h"),
                Include(file=Path("file4"), include="foo/nested/bar.h"),
                Include(file=Path("file4"), include="baz_some_partial_name.h"),
                Include(file=Path("file5"), include="bar/match_something_inside_include.h"),
                Include(file=Path("file6"), include="matching_begin_works_without_regex"),
                Include(file=Path("file7"), include="without_regex_no_substring_match"),
                Include(file=Path("file8"), include="without_regex_no_matching_end"),
            ],
            ignored_includes=IgnoredIncludes(
                paths=[],
                patterns=[
                    "foo/.*",
                    ".*_partial_name.h",
                    ".*_something_inside_.*",
                    "substring",
                    "matching_begin",
                    "matching_end",
                ],
            ),
        )

        self.assertEqual(len(result), 4)
        self.assertTrue(Include(file=Path("file1"), include="some_header.h") in result)
        self.assertTrue(Include(file=Path("file2"), include="foo.h") in result)
        self.assertTrue(Include(file=Path("file7"), include="without_regex_no_substring_match") in result)
        self.assertTrue(Include(file=Path("file8"), include="without_regex_no_matching_end") in result)


class TestGetIncludesFromFile(unittest.TestCase):
    def test_single_include(self):
        test_file = Path("src/analyze_includes/test/data/another_header.h")
        result = get_includes_from_file(test_file)

        self.assertEqual(result, [Include(file=test_file, include="foo/bar.h")])

    def test_multiple_includes(self):
        test_file = Path("src/analyze_includes/test/data/some_header.h")
        result = get_includes_from_file(test_file)

        self.assertEqual(len(result), 4)
        self.assertTrue(Include(file=test_file, include="bar.h") in result)
        self.assertTrue(Include(file=test_file, include="foo/bar/baz.h") in result)
        self.assertTrue(Include(file=test_file, include="some/path/to_a/system_header.h") in result)

    def test_commented_includes_single_line_comments(self):
        test_file = Path("src/analyze_includes/test/data/commented_includes/single_line_comments.h")
        result = get_includes_from_file(test_file)

        self.assertEqual(len(result), 2)
        self.assertTrue(Include(file=test_file, include="active_a.h") in result)
        self.assertTrue(Include(file=test_file, include="active_b.h") in result)

    def test_commented_includes_block_comments(self):
        test_file = Path("src/analyze_includes/test/data/commented_includes/block_comments.h")
        result = get_includes_from_file(test_file)

        self.assertEqual(len(result), 8)
        self.assertTrue(Include(file=test_file, include="active_a.h") in result)
        self.assertTrue(Include(file=test_file, include="active_b.h") in result)
        self.assertTrue(Include(file=test_file, include="active_c.h") in result)
        self.assertTrue(Include(file=test_file, include="active_d.h") in result)
        self.assertTrue(Include(file=test_file, include="active_e.h") in result)
        self.assertTrue(Include(file=test_file, include="active_f.h") in result)
        self.assertTrue(Include(file=test_file, include="active_g.h") in result)
        self.assertTrue(Include(file=test_file, include="active_h.h") in result)

    def test_commented_includes_mixed_style(self):
        test_file = Path("src/analyze_includes/test/data/commented_includes/mixed_style.h")
        result = get_includes_from_file(test_file)

        self.assertEqual(result, [Include(file=test_file, include="active.h")])

    def test_if_def_conditional_includes(self):
        test_file = Path("src/analyze_includes/test/data/conditional_includes/if_def_style.h")
        result = get_includes_from_file(test_file, ["-DFOO"])
        self.assertEqual(len(result), 3)
        self.assertTrue(Include(file=test_file, include="foo.h") in result)
        self.assertTrue(Include(file=test_file, include="bar.h") in result)
        self.assertTrue(Include(file=test_file, include="baz.h") in result)

        result = get_includes_from_file(test_file, ["-DFOO", "-U FOO"])
        self.assertEqual(len(result), 2)
        self.assertFalse(Include(file=test_file, include="foo.h") in result)
        self.assertTrue(Include(file=test_file, include="bar.h") in result)

        result = get_includes_from_file(test_file, ["-DNOBAR"])
        self.assertEqual(len(result), 2)
        self.assertTrue(Include(file=test_file, include="nobar.h") in result)
        self.assertTrue(Include(file=test_file, include="baz.h") in result)

    def test_if_defined_conditional_includes(self):
        test_file = Path("src/analyze_includes/test/data/conditional_includes/if_defined_style.cc")
        result = get_includes_from_file(test_file, ["-DFOO"])
        self.assertEqual(len(result), 3)
        self.assertTrue(Include(file=test_file, include="foo.h") in result)
        self.assertTrue(Include(file=test_file, include="bar.h") in result)
        self.assertTrue(Include(file=test_file, include="iostream") in result)

        result = get_includes_from_file(test_file, ["-DNOBAR=1"])
        self.assertEqual(len(result), 2)
        self.assertTrue(Include(file=test_file, include="nobar.h") in result)
        self.assertTrue(Include(file=test_file, include="iostream") in result)

    def test_if_value_conditional_includes(self):
        test_file = Path("src/analyze_includes/test/data/conditional_includes/if_value_style.h")
        result = get_includes_from_file(test_file, ["-DFOO=0"])
        self.assertEqual(len(result), 2)
        self.assertTrue(Include(file=test_file, include="nobar.h") in result)
        self.assertTrue(Include(file=test_file, include="baz_is_not_3.h") in result)

        result = get_includes_from_file(test_file, ["-DFOO=1", "-D BAR=2", "-DBAZ=3"])
        self.assertEqual(len(result), 2)
        self.assertTrue(Include(file=test_file, include="foo.h") in result)
        self.assertTrue(Include(file=test_file, include="bar2.h") in result)


class TestGetRelevantIncludesFromFiles(unittest.TestCase):
    def test_get_relevant_includes_from_files(self):
        result = get_relevant_includes_from_files(
            files=["src/analyze_includes/test/data/some_header.h", "src/analyze_includes/test/data/another_header.h"],
            ignored_includes=IgnoredIncludes(paths=["vector"], patterns=[]),
        )

        self.assertEqual(len(result), 4)
        self.assertTrue(Include(file=Path("src/analyze_includes/test/data/some_header.h"), include="bar.h") in result)
        self.assertTrue(
            Include(file=Path("src/analyze_includes/test/data/some_header.h"), include="foo/bar/baz.h") in result
        )
        self.assertTrue(
            Include(file=Path("src/analyze_includes/test/data/some_header.h"), include="some/path/to_a/system_header.h")
            in result
        )
        self.assertTrue(
            Include(file=Path("src/analyze_includes/test/data/another_header.h"), include="foo/bar.h") in result
        )


if __name__ == "__main__":
    unittest.main()
