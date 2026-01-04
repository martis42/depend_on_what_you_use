load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")
load("//dwyu/aspect:dwyu.bzl", "extract_cpp_standard_from_compiler_flags", "extract_defines_from_compiler_flags")

def _extract_defines_from_compiler_flags_test_impl(ctx):
    env = unittest.begin(ctx)

    # Macro without value
    asserts.equals(env, ["Bar"], extract_defines_from_compiler_flags(["--foo", "-DBar", "whatever"]))
    asserts.equals(env, ["Bar"], extract_defines_from_compiler_flags(["--foo", "--define-macro=Bar", "whatever"]))
    asserts.equals(env, ["Bar"], extract_defines_from_compiler_flags(["--foo", "--define-macro", "Bar", "whatever"]))
    asserts.equals(env, ["Bar"], extract_defines_from_compiler_flags(["--foo", "/DBar", "whatever"]))

    # Macro with integer value
    asserts.equals(env, ["Foo=42"], extract_defines_from_compiler_flags(["--foo", "-DFoo=42", "whatever"]))
    asserts.equals(env, ["Foo=42"], extract_defines_from_compiler_flags(["--foo", "--define-macro=Foo=42", "whatever"]))
    asserts.equals(env, ["Foo=42"], extract_defines_from_compiler_flags(["--foo", "--define-macro", "Foo=42", "whatever"]))
    asserts.equals(env, ["Foo=42"], extract_defines_from_compiler_flags(["--foo", "/DFoo=42", "whatever"]))

    # Macro with string value
    asserts.equals(env, ['Foo="bar"'], extract_defines_from_compiler_flags(["--foo", '-DFoo="bar"', "whatever"]))
    asserts.equals(env, ['Foo="bar"'], extract_defines_from_compiler_flags(["--foo", '--define-macro=Foo="bar"', "whatever"]))
    asserts.equals(env, ['Foo="bar"'], extract_defines_from_compiler_flags(["--foo", "--define-macro", 'Foo="bar"', "whatever"]))
    asserts.equals(env, ['Foo="bar"'], extract_defines_from_compiler_flags(["--foo", '/DFoo="bar"', "whatever"]))

    # Escape double quoted input
    asserts.equals(env, ['Foo=\"bar\"'], extract_defines_from_compiler_flags(['-DFoo=\\"bar\\"']))

    # Deduplicate macros
    asserts.equals(env, ["Bar", "Foo"], extract_defines_from_compiler_flags(["-DBar", "-DBar", "-DFoo"]))

    # Macros overwrite each other
    asserts.equals(env, ["Foo=1337"], extract_defines_from_compiler_flags(["-DFoo", "-DFoo=42", "-DFoo=1337"]))

    # Undefine another macro
    asserts.equals(env, ["Bar"], extract_defines_from_compiler_flags(["-DFoo", "-UFoo", "-DBar"]))
    asserts.equals(env, ["Bar"], extract_defines_from_compiler_flags(["-DFoo", "--undefine-macro=Foo", "-DBar"]))
    asserts.equals(env, ["Bar"], extract_defines_from_compiler_flags(["-DFoo", "--undefine-macro", "Foo", "-DBar"]))
    asserts.equals(env, ["Bar"], extract_defines_from_compiler_flags(["/DFoo", "/UFoo", "/DBar"]))
    asserts.equals(env, ["Bar"], extract_defines_from_compiler_flags(["/DFoo", "/uFoo", "/DBar"]))

    # Undefine another macro with value
    asserts.equals(env, [], extract_defines_from_compiler_flags(["-DFoo=42", "-UFoo"]))

    # Define previously undefined macro
    asserts.equals(env, ["Foo=42"], extract_defines_from_compiler_flags(["-UFoo", "-DFoo=42"]))

    return unittest.end(env)

def _extract_cpp_standard_from_compiler_flags_test_impl(ctx):
    env = unittest.begin(ctx)

    # None if empty list is provided
    asserts.equals(env, "unknown", extract_cpp_standard_from_compiler_flags([]))

    # None if nothing can be found
    asserts.equals(env, "unknown", extract_cpp_standard_from_compiler_flags(["whatever"]))

    # Last definition wins
    asserts.equals(env, "98", extract_cpp_standard_from_compiler_flags(["-std=c++20", "whatever", "-std=c++98"]))

    # Gcc/Clang CLI style
    asserts.equals(env, "20", extract_cpp_standard_from_compiler_flags(["-std=c++20"]))
    asserts.equals(env, "17", extract_cpp_standard_from_compiler_flags(["--std=c++17"]))
    asserts.equals(env, "14", extract_cpp_standard_from_compiler_flags(["--std", "c++14"]))

    # MSVC style CLI style
    asserts.equals(env, "23", extract_cpp_standard_from_compiler_flags(["/std:c++23"]))

    # Amendments versions
    asserts.equals(env, "11", extract_cpp_standard_from_compiler_flags(["-std=c++0x"]))
    asserts.equals(env, "14", extract_cpp_standard_from_compiler_flags(["-std=cc++1y"]))
    asserts.equals(env, "17", extract_cpp_standard_from_compiler_flags(["-std=c++1z"]))
    asserts.equals(env, "20", extract_cpp_standard_from_compiler_flags(["-std=c++2a"]))
    asserts.equals(env, "23", extract_cpp_standard_from_compiler_flags(["-std=c++2b"]))
    asserts.equals(env, "26", extract_cpp_standard_from_compiler_flags(["-std=c++2c"]))

    # GNU variants
    asserts.equals(env, "20", extract_cpp_standard_from_compiler_flags(["-std=gnu++20"]))
    asserts.equals(env, "14", extract_cpp_standard_from_compiler_flags(["-std=gnu++1y"]))

    # MVSC variants
    asserts.equals(env, "23", extract_cpp_standard_from_compiler_flags(["/std:c++23preview"]))
    asserts.equals(env, "latest", extract_cpp_standard_from_compiler_flags(["/std:c++latest"]))

    # Unknown for bogus input
    asserts.equals(env, "unknown", extract_cpp_standard_from_compiler_flags(["-std=foo"]))
    asserts.equals(env, "unknown", extract_cpp_standard_from_compiler_flags(["-std=c++1g"]))
    asserts.equals(env, "unknown", extract_cpp_standard_from_compiler_flags(["/std:c++23bar"]))

    return unittest.end(env)

extract_defines_from_compiler_flags_test = unittest.make(_extract_defines_from_compiler_flags_test_impl)
extract_cpp_standard_from_compiler_flags_test = unittest.make(_extract_cpp_standard_from_compiler_flags_test_impl)

def dwyu_aspect_test_suite(name):
    unittest.suite(
        name,
        extract_defines_from_compiler_flags_test,
        extract_cpp_standard_from_compiler_flags_test,
    )
