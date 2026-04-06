load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")

def rules_cc_hashing(input):
    hash_int = hash(input)
    return "%x" % hash_int

def _hash_test_impl(ctx):
    """
    In our Python implementation we have to replicate the behavior of the Starlark hash function to be able to
    deduce the correct path at which virtual headers can be found.
    To ensure that our Python implementation behaves exactly like the Starlark implementation, we test the same
    values both in Python and in Starlark.

    Keep this test in sync with with dwyu/apply_fixes/test/hash_test.py
    """
    env = unittest.begin(ctx)

    asserts.equals(env, "0", rules_cc_hashing(""))
    asserts.equals(env, "391a65ad", rules_cc_hashing("abcdefghijklmnopqrstuvwxyz"))
    asserts.equals(env, "5e774605", rules_cc_hashing("0123456789"))
    asserts.equals(env, "ed32c55a", rules_cc_hashing("foobarfoobar"))
    asserts.equals(env, "c7eb19d4", rules_cc_hashing("SOME_BIG_CHARACTERS"))
    asserts.equals(env, "be34c469", rules_cc_hashing("with_special_%&$#@!_characters"))

    return unittest.end(env)

foo_test = unittest.make(_hash_test_impl)

def hash_test_suite(name):
    unittest.suite(name, foo_test)
