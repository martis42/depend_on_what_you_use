import unittest
from unittest.mock import patch

from dwyu.apply_fixes.cli import cli


class TestCli(unittest.TestCase):
    @patch("sys.argv", ["prog"])
    def test_no_fix_option_aborts(self) -> None:
        with self.assertLogs(level="FATAL") as captured_logs, self.assertRaises(SystemExit) as exit_ctx:
            cli()

        self.assertEqual(exit_ctx.exception.code, 1)
        self.assertEqual(captured_logs.output, ["CRITICAL:root:Please choose at least one of the 'fix-..' options"])

    @patch("sys.argv", ["prog", "--fix-all"])
    def test_fix_all_is_accepted(self) -> None:
        args = cli()

        self.assertTrue(args.fix_all)

    @patch("sys.argv", ["prog", "--fix-unused-deps"])
    def test_fix_unused_deps_is_accepted(self) -> None:
        args = cli()

        self.assertTrue(args.fix_unused_deps)

    @patch("sys.argv", ["prog", "--fix-deps-which-should-be-private"])
    def test_fix_deps_which_should_be_private_is_accepted(self) -> None:
        args = cli()

        self.assertTrue(args.fix_deps_which_should_be_private)

    @patch("sys.argv", ["prog", "--fix-missing-deps"])
    def test_fix_missing_deps_is_accepted(self) -> None:
        args = cli()

        self.assertTrue(args.fix_missing_deps)


if __name__ == "__main__":
    unittest.main()
