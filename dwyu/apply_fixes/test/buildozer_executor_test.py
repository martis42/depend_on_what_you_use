import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from dwyu.apply_fixes.buildozer_executor import BuildozerExecutor


class TestBuildozerExecutor(unittest.TestCase):
    def test_make_simple_base_command(self) -> None:
        unit = BuildozerExecutor(buildozer="foo", buildozer_args=[], workspace=Path(), dry=False)
        self.assertEqual(unit._base_cmd, ["foo"])  # noqa: SLF001

    def test_make_complex_base_command(self) -> None:
        unit = BuildozerExecutor(buildozer="foo", buildozer_args=["riff", "raff"], workspace=Path(), dry=True)
        self.assertEqual(unit._base_cmd, ["foo", "riff", "raff", "-stdout"])  # noqa: SLF001

    @patch("dwyu.apply_fixes.buildozer_executor.system", return_value="Windows")
    def test_adapt_target_to_platform_windows(self, _: MagicMock) -> None:
        self.assertEqual(
            BuildozerExecutor.adapt_target_to_platform("//foo/bar:baz"),
            "//foo\\bar:baz",
        )

    @patch("dwyu.apply_fixes.buildozer_executor.system", return_value="Linux")
    def test_adapt_target_to_platform_linux(self, _: MagicMock) -> None:
        self.assertEqual(
            BuildozerExecutor.adapt_target_to_platform("//foo/bar:baz"),
            "//foo/bar:baz",
        )


if __name__ == "__main__":
    unittest.main()
