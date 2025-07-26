import unittest
from pathlib import Path

from dwyu.cc_toolchain_headers.private.gather_cc_toolchain_headers import (
    extract_include_paths_from_gcc_like_output,
    gather_toolchain_headers,
)


class TestExtractIncludePathsFromGccLikeOutput(unittest.TestCase):
    def test_empty_input(self) -> None:
        result = extract_include_paths_from_gcc_like_output("")
        self.assertEqual(result, [])

    def test_parse_input(self) -> None:
        result = extract_include_paths_from_gcc_like_output(
            """
Unrelated stuff

#include "..." search starts here:
 path/a
 path/a/aa
#include <...> search starts here:
 path/b
 path/c
End of search list.
unrelated/path
"""
        )
        self.assertEqual(result, [Path("path/a"), Path("path/a/aa"), Path("path/b"), Path("path/c")])


class TestGatherBuiltInHeaders(unittest.TestCase):
    def test_empty_input(self) -> None:
        result = gather_toolchain_headers([])
        self.assertEqual(result, [])

    def test_filter_and_gather_files(self) -> None:
        result = gather_toolchain_headers(
            [
                Path("dwyu/cc_toolchain_headers/private/test/data/include_root"),
                Path("dwyu/cc_toolchain_headers/private/test/data/include_root/bar"),
            ]
        )

        expected = ["bar/bar.h", "bar.h", "relevant_no_extension", "relevant.h", "foo/header.hpp"]
        self.assertEqual(sorted(result), sorted(expected))


if __name__ == "__main__":
    unittest.main()
