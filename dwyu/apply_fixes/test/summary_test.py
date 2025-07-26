import unittest

from dwyu.apply_fixes.summary import Summary


class TestSummary(unittest.TestCase):
    def test_add_succeeding_command(self) -> None:
        unit = Summary()
        unit.add_command(cmd=["foo", "bar"], buildozer_result=0)
        self.assertEqual(unit.successful_fixes, [["foo", "bar"]])

    def test_add_command_without_effect(self) -> None:
        unit = Summary()
        unit.add_command(cmd=["foo", "bar"], buildozer_result=3)
        self.assertEqual(unit.fixes_without_effect, [["foo", "bar"]])

    def test_add_failing_command(self) -> None:
        unit = Summary()
        unit.add_command(cmd=["foo", "bar"], buildozer_result=2)
        self.assertEqual(unit.failed_fixes, [["foo", "bar"]])

    def test_raise_on_unexpected_return_code(self) -> None:
        unit = Summary()
        with self.assertRaisesRegex(Exception, "failed with the unexpected return code"):
            unit.add_command(cmd=["foo", "bar"], buildozer_result=5)


if __name__ == "__main__":
    unittest.main()
