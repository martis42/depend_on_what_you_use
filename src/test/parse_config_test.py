import unittest
from pathlib import Path

from src.parse_config import load_config


class TestLoadConfig(unittest.TestCase):
    def test_load_empty(self):
        ignored_inclues, extra_ignoredf_includes = load_config(Path("src/test/data/config_empty.json"))

        self.assertEqual(ignored_inclues, [])
        self.assertEqual(extra_ignoredf_includes, [])

    def test_load_config(self):
        ignored_includes, extra_ignored_includes = load_config(Path("src/test/data/config.json"))

        self.assertEqual(len(ignored_includes), 2)
        self.assertTrue("foo" in ignored_includes)
        self.assertTrue("bar" in ignored_includes)
        self.assertEqual(len(extra_ignored_includes), 2)
        self.assertTrue("wup" in extra_ignored_includes)
        self.assertTrue("wupwup" in extra_ignored_includes)


if __name__ == "__main__":
    unittest.main()
