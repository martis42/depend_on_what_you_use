load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")
load("//src/toolchain_headers/private:gather_toolchain_headers.bzl", "extract_include_paths")

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

    # Gcc and clang API compilers
    for compiler in ["clang", "clang-foo", "gcc", "specialgcc"]:
        asserts.equals(
            env,
            ["foo/bar", "foo", "bar"],
            extract_include_paths(cmd = ["-unrelated", "tik", "-I", "foo/bar", "-iquote", "foo", "-isystem", "bar"], compiler = compiler),
        )

    # MSCV API input
    for compiler in ["msvc", "msvc-foo", "some_msvc"]:
        asserts.equals(env, ["foo"], extract_include_paths(cmd = ["/I", "foo", "/Unrelated", "bar"], compiler = compiler))

    return unittest.end(env)

extract_include_paths_from_compiler_command_test = unittest.make(_extract_include_paths_from_compiler_command_test_impl)

def extract_include_paths_test_suite(name):
    unittest.suite(name, extract_include_paths_from_compiler_command_test)
