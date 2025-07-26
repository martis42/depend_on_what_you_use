import unittest

from dwyu.apply_fixes.utils import args_string_to_list


class TestArgsStringToList(unittest.TestCase):
    def test_no_args(self) -> None:
        self.assertEqual(args_string_to_list(None), [])
        self.assertEqual(args_string_to_list(""), [])

    def test_single_arg(self) -> None:
        self.assertEqual(args_string_to_list("foo"), ["foo"])

    def test_multiple_args(self) -> None:
        self.assertEqual(args_string_to_list("--foo --bar=42 baz 1337"), ["--foo", "--bar=42", "baz", "1337"])


if __name__ == "__main__":
    unittest.main()
