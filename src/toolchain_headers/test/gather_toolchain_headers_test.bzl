load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")
load("//src/toolchain_headers:gather_toolchain_headers.bzl", "extract_include_paths")

def _extract_include_paths_from_compiler_command_test_impl(ctx):
    env = unittest.begin(ctx)

    # Empty input
    asserts.equals(env, [], extract_include_paths(cmd = [], compiler = "gcc"))

    # Include flag without value
    asserts.equals(env, [], extract_include_paths(cmd = ["-I"], compiler = "gcc"))

    # Aggregate multiple appearances
    asserts.equals(env, ["foo", "bar"], extract_include_paths(cmd = ["-I", "foo", "-I", "bar"], compiler = "gcc"))

    # Deduplicate results
    asserts.equals(env, ["foo"], extract_include_paths(cmd = ["-I", "foo", "-I", "foo"], compiler = "gcc"))

    # Only consider one value after include path flag
    asserts.equals(env, ["foo"], extract_include_paths(cmd = ["-I", "foo", "other"], compiler = "gcc"))

    gcc_and_clang_api_test = ["-unrelated", "tik", "-I", "foo/bar", "-iquote", "foo", "-isystem", "bar"]
    gcc_and_clang_api_expected = ["foo/bar", "foo", "bar"]

    # Gcc and clang API compilers
    for compiler in ["clang", "clang-cl", "emscripten", "gcc", "mingw-gcc"]:
        asserts.equals(env, gcc_and_clang_api_expected, extract_include_paths(cmd = gcc_and_clang_api_test, compiler = compiler))

    # MSCV input
    asserts.equals(env, ["foo"], extract_include_paths(cmd = ["/I", "foo", "/Unrelated", "bar"], compiler = "msvc-cl"))

    return unittest.end(env)

extract_include_paths_from_compiler_command_test = unittest.make(_extract_include_paths_from_compiler_command_test_impl)

def gather_toolchain_headers_test_suite(name):
    unittest.suite(name, extract_include_paths_from_compiler_command_test)
