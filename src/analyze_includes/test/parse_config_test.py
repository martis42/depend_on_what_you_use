import unittest
from pathlib import Path

from src.analyze_includes.parse_config import get_ignored_includes
from src.analyze_includes.std_header import STD_HEADER


class TestGetIgnoredIncludes(unittest.TestCase):
    def test_no_config_and_no_system_headers_info_provided(self) -> None:
        ignored_includes = get_ignored_includes(config_file=None, toolchain_headers_info=None)

        self.assertEqual(ignored_includes.paths, STD_HEADER)
        self.assertEqual(ignored_includes.patterns, [])

    def test_system_headers_info_replaces_hard_coded_headers(self) -> None:
        ignored_includes = get_ignored_includes(
            config_file=None,
            toolchain_headers_info=Path("src/analyze_includes/test/data/config/system_headers_info.json"),
        )

        self.assertEqual(ignored_includes.paths, {"foo/bar.h", "some_header"})
        self.assertEqual(ignored_includes.patterns, [])

    def test_empty_config_file(self) -> None:
        ignored_includes = get_ignored_includes(
            config_file=Path("src/analyze_includes/test/data/config/empty.json"),
            toolchain_headers_info=Path("src/analyze_includes/test/data/config/system_headers_info.json"),
        )

        self.assertEqual(ignored_includes.paths, {"foo/bar.h", "some_header"})
        self.assertEqual(ignored_includes.patterns, [])

    def test_extra_ignore_paths(self) -> None:
        ignored_includes = get_ignored_includes(
            config_file=Path("src/analyze_includes/test/data/config/extra_ignore_paths.json"),
            toolchain_headers_info=Path("src/analyze_includes/test/data/config/system_headers_info.json"),
        )

        self.assertEqual(ignored_includes.paths, {"foo/bar.h", "some_header", "foo", "bar"})
        self.assertEqual(ignored_includes.patterns, [])

    def test_override_default_ignore_patterns(self) -> None:
        ignored_includes = get_ignored_includes(
            config_file=Path("src/analyze_includes/test/data/config/overwrite_default_ignore_paths.json"),
            toolchain_headers_info=Path("src/analyze_includes/test/data/config/system_headers_info.json"),
        )

        self.assertEqual(ignored_includes.paths, {"foo", "bar", "foobar"})
        self.assertEqual(ignored_includes.patterns, [])

    def test_ignore_patterns(self) -> None:
        ignored_includes = get_ignored_includes(
            config_file=Path("src/analyze_includes/test/data/config/ignore_patterns.json"), toolchain_headers_info=None
        )

        self.assertEqual(ignored_includes.paths, STD_HEADER)
        self.assertEqual(ignored_includes.patterns, ["foo", "bar"])


if __name__ == "__main__":
    unittest.main()
