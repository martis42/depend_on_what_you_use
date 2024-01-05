import unittest
from pathlib import Path

from src.analyze_includes.parse_config import get_ignored_includes
from src.analyze_includes.std_header import STD_HEADER


class TestGetIgnoredIncludes(unittest.TestCase):
    def test_no_config_file_provided(self) -> None:
        ignored_includes = get_ignored_includes(None)

        self.assertEqual(ignored_includes.paths, list(STD_HEADER))
        self.assertEqual(ignored_includes.patterns, [])

    def test_empty_config_file(self) -> None:
        ignored_includes = get_ignored_includes(Path("src/analyze_includes/test/data/config/empty.json"))

        self.assertEqual(ignored_includes.paths, list(STD_HEADER))
        self.assertEqual(ignored_includes.patterns, [])

    def test_extra_ignore_paths(self) -> None:
        ignored_includes = get_ignored_includes(Path("src/analyze_includes/test/data/config/extra_ignore_paths.json"))

        self.assertEqual(len(ignored_includes.paths), len(list(STD_HEADER)) + 2)
        self.assertTrue("foo" in ignored_includes.paths)
        self.assertTrue("bar" in ignored_includes.paths)
        self.assertEqual(ignored_includes.patterns, [])

    def test_override_default_ignore_patterns(self) -> None:
        ignored_includes = get_ignored_includes(
            Path("src/analyze_includes/test/data/config/overwrite_default_ignore_paths.json")
        )

        self.assertEqual(len(ignored_includes.paths), 3)
        self.assertTrue("foo" in ignored_includes.paths)
        self.assertTrue("bar" in ignored_includes.paths)
        self.assertTrue("foobar" in ignored_includes.paths)
        self.assertEqual(ignored_includes.patterns, [])

    def test_ignore_patterns(self) -> None:
        ignored_includes = get_ignored_includes(Path("src/analyze_includes/test/data/config/ignore_patterns.json"))

        self.assertEqual(ignored_includes.paths, list(STD_HEADER))
        self.assertEqual(ignored_includes.patterns, ["foo", "bar"])


if __name__ == "__main__":
    unittest.main()
