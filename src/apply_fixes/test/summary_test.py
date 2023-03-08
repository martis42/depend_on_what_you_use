import unittest

from src.apply_fixes.summary import Summary


class TestSummary(unittest.TestCase):
    def test_add_succeeding_command(self):
        unit = Summary()
        unit.add_command(cmd=["foo", "bar"], buildozer_result=0)
        self.assertEqual(unit.succesful_fixes, [["foo", "bar"]])

    def test_add_command_without_effect(self):
        unit = Summary()
        unit.add_command(cmd=["foo", "bar"], buildozer_result=3)
        self.assertEqual(unit.fixes_without_effect, [["foo", "bar"]])

    def test_add_failing_command(self):
        unit = Summary()
        unit.add_command(cmd=["foo", "bar"], buildozer_result=2)
        self.assertEqual(unit.failed_fixes, [["foo", "bar"]])

    def test_raise_on_unexpected_return_code(self):
        unit = Summary()
        with self.assertRaises(Exception):
            unit.add_command(cmd=["foo", "bar"], buildozer_result=5)


if __name__ == "__main__":
    unittest.main()
