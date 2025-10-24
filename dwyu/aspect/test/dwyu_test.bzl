load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")
load("//dwyu/aspect:dwyu.bzl", "extract_cpp_standard_from_compiler_flags", "extract_defines_from_compiler_flags")

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

    # Escape double quoted input
    asserts.equals(env, ['Foo=\"bar\"'], extract_defines_from_compiler_flags(['-DFoo=\\"bar\\"']))

    # Define with complex value
    asserts.equals(
        env,
        ["Foo=BAR=42", "Tick 42", 'Riff "Raff"'],
        extract_defines_from_compiler_flags(["-DFoo=BAR=42", "-DTick 42", '-DRiff "Raff"']),
    )

    # MSVC syntax
    asserts.equals(
        env,
        ["Bar", "FooBar=42"],
        extract_defines_from_compiler_flags(["/DFoo", "/UFoo", "/DBar", "/DFooBar=42"]),
    )

    return unittest.end(env)

def _extract_cpp_standard_from_compiler_flags_test_impl(ctx):
    env = unittest.begin(ctx)

    # None if empty list is provided
    asserts.equals(env, None, extract_cpp_standard_from_compiler_flags([]))

    # None if nothing can be found
    asserts.equals(env, None, extract_cpp_standard_from_compiler_flags(["whatever"]))

    # Unknown standard value yields 1
    asserts.equals(env, 1, extract_cpp_standard_from_compiler_flags(["whatever", "-std=foo"]))

    # Basic case
    asserts.equals(env, 202002, extract_cpp_standard_from_compiler_flags(["-std=c++20", "whatever"]))

    # Last definition wins
    asserts.equals(env, 199711, extract_cpp_standard_from_compiler_flags(["-std=c++20", "whatever", "-std=c++98"]))

    # MSVC syntax
    asserts.equals(env, 202302, extract_cpp_standard_from_compiler_flags(["/std:c++23"]))

    return unittest.end(env)

extract_defines_from_compiler_flags_test = unittest.make(_extract_defines_from_compiler_flags_test_impl)
extract_cpp_standard_from_compiler_flags_test = unittest.make(_extract_cpp_standard_from_compiler_flags_test_impl)

def dwyu_aspect_test_suite(name):
    unittest.suite(
        name,
        extract_defines_from_compiler_flags_test,
        extract_cpp_standard_from_compiler_flags_test,
    )
