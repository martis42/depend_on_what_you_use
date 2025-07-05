import unittest
from pathlib import Path

from src.toolchain_headers.private.gather_toolchain_headers import gather_built_in_headers, gather_toolchain_headers


class TestGatherToolchainHeaders(unittest.TestCase):
    def test_empty_input(self) -> None:
        result = gather_toolchain_headers(toolchain_files=[], toolchain_include_dirs=[])
        self.assertEqual(result, [])

    def test_no_files(self) -> None:
        result = gather_toolchain_headers(toolchain_files=[], toolchain_include_dirs=[Path("foo/bar")])
        self.assertEqual(result, [])

    def test_no_include_directories(self) -> None:
        result = gather_toolchain_headers(toolchain_files=[Path("some/file")], toolchain_include_dirs=[])
        self.assertEqual(result, [])

    def test_filter_and_gather_files(self) -> None:
        result = gather_toolchain_headers(
            toolchain_files=[
                Path("unrelated_file.h"),
                Path("foo/no_extension_header"),
                Path("foo/sub/dir/header.hh"),
                Path("foo/duplicated/header.h"),
                Path("foo/.undesired_file"),
                Path("tik/unrelated_file.h"),
                Path("tik/tok/other_header.hpp"),
                Path("tik/tok/unrelated_file.txt"),
                Path("tik/tok/duplicated/header.h"),
            ],
            toolchain_include_dirs=[Path("foo"), Path("tik/tok")],
        )

        expected = [
            "no_extension_header",
            "sub/dir/header.hh",
            "duplicated/header.h",
            "other_header.hpp",
            "duplicated/header.h",
        ]
        self.assertEqual(sorted(result), sorted(expected))


class TestGatherBuiltInHeaders(unittest.TestCase):
    def test_empty_input(self) -> None:
        result = gather_built_in_headers([])
        self.assertEqual(result, [])

    def test_filter_and_gather_files(self) -> None:
        result = gather_built_in_headers(
            [
                Path("src/toolchain_headers/private/test/data/other_dir"),
                Path("src/toolchain_headers/private/test/data/some/dir"),
            ]
        )

        expected = ["no_extension", "relevant.h", "header.hpp", "sub/dir/header.hh"]
        self.assertEqual(sorted(result), sorted(expected))


if __name__ == "__main__":
    unittest.main()
