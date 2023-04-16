load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")
load("//src/aspect:dwyu.bzl", "extract_defines_from_compiler_flags")

def _extract_defines_from_compiler_flags_test_impl(ctx):
    env = unittest.begin(ctx)

    # Basic case
    asserts.equals(env, ["Bar"], extract_defines_from_compiler_flags(["--foo", "-DBar", "whatever"]))

    # Deduplicate defines
    asserts.equals(env, ["Bar", "Foo"], extract_defines_from_compiler_flags(["-DBar", "-DBar", "-DFoo"]))

    # Defines overwrite each other
    asserts.equals(env, ["Foo=1337"], extract_defines_from_compiler_flags(["-DFoo", "-DFoo=42", "-DFoo=1337"]))

    # Undefine another define
    asserts.equals(env, ["Bar"], extract_defines_from_compiler_flags(["-DFoo", "-UFoo", "-DBar"]))

    # Undefine another define with value
    asserts.equals(env, [], extract_defines_from_compiler_flags(["-DFoo=42", "-UFoo"]))

    # Define previously undefined value
    asserts.equals(env, ["Foo=42"], extract_defines_from_compiler_flags(["-UFoo", "-DFoo=42"]))

    # Define with complex value
    asserts.equals(
        env,
        ["Foo=BAR=42", "Tick 42", 'Riff "Raff"'],
        extract_defines_from_compiler_flags(["-DFoo=BAR=42", "-DTick 42", '-DRiff "Raff"']),
    )

    return unittest.end(env)

extract_defines_from_compiler_flags_test = unittest.make(_extract_defines_from_compiler_flags_test_impl)

def dwyu_aspect_test_suite(name):
    unittest.suite(
        name,
        extract_defines_from_compiler_flags_test,
    )
