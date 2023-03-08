import unittest

from src.apply_fixes.apply_fixes import get_file_name, target_to_file, target_to_package


class TestApplyFixesHelper(unittest.TestCase):
    def test_get_file_name(self):
        self.assertEqual(get_file_name("foo"), "foo")
        self.assertEqual(get_file_name("foo.txt"), "foo.txt")
        self.assertEqual(get_file_name("riff/raff/foo.txt"), "foo.txt")

    def test_target_to_file(self):
        self.assertEqual(target_to_file(":foo"), "foo")
        self.assertEqual(target_to_file("@foo//bar:riff/raff.txt"), "raff.txt")

    def test_target_to_package(self):
        self.assertEqual(target_to_package(":foo"), "")
        self.assertEqual(target_to_package("@foo//bar:riff/raff"), "@foo//bar")


if __name__ == "__main__":
    unittest.main()
