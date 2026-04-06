import unittest

from dwyu.apply_fixes.search_missing_deps import starlark_hash_as_hex_string


class TestHashing(unittest.TestCase):
    def test_hashing_works_like_in_starlark(self) -> None:
        """
        In our Python implementation we have to replicate the behavior of the Starlark hash function to be able to
        deduce the correct path at which virtual headers can be found.
        To ensure that our Python implementation behaves exactly like the Starlark implementation, we test the same
        values both in Python and in Starlark.

        Keep this test in sync with dwyu/apply_fixes/test/hash_test.bzl.
        """

        self.assertEqual(starlark_hash_as_hex_string(""), "0")
        self.assertEqual(starlark_hash_as_hex_string("abcdefghijklmnopqrstuvwxyz"), "391a65ad")
        self.assertEqual(starlark_hash_as_hex_string("0123456789"), "5e774605")
        self.assertEqual(starlark_hash_as_hex_string("foobarfoobar"), "ed32c55a")
        self.assertEqual(starlark_hash_as_hex_string("SOME_BIG_CHARACTERS"), "c7eb19d4")
        self.assertEqual(starlark_hash_as_hex_string("with_special_%&$#@!_characters"), "be34c469")


if __name__ == "__main__":
    unittest.main()
