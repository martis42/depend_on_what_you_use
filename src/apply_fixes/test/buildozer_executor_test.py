import unittest

from src.apply_fixes.buildozer_executor import BuildozerExecutor


class TestBuildozerExecutor(unittest.TestCase):
    def test_make_simple_base_command(self):
        unit = BuildozerExecutor(buildozer="foo", buildozer_args=[], workspace=None, dry=False)
        self.assertEqual(unit._base_cmd, ["foo"])

    def test_make_complex_base_command(self):
        unit = BuildozerExecutor(buildozer="foo", buildozer_args=["riff", "raff"], workspace=None, dry=True)
        self.assertEqual(unit._base_cmd, ["foo", "riff", "raff", "-stdout"])


if __name__ == "__main__":
    unittest.main()
