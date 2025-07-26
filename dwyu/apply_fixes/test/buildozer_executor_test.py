import unittest
from pathlib import Path

from dwyu.apply_fixes.buildozer_executor import BuildozerExecutor


class TestBuildozerExecutor(unittest.TestCase):
    def test_make_simple_base_command(self) -> None:
        unit = BuildozerExecutor(buildozer="foo", buildozer_args=[], workspace=Path(), dry=False)
        self.assertEqual(unit._base_cmd, ["foo"])  # noqa: SLF001

    def test_make_complex_base_command(self) -> None:
        unit = BuildozerExecutor(buildozer="foo", buildozer_args=["riff", "raff"], workspace=Path(), dry=True)
        self.assertEqual(unit._base_cmd, ["foo", "riff", "raff", "-stdout"])  # noqa: SLF001


if __name__ == "__main__":
    unittest.main()
