load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")
load("//dwyu/cc_toolchain_headers/private:gather_cc_toolchain_headers.bzl", "extract_msvc_include_paths")

def _extract_msvc_include_paths_test_impl(ctx):
    env = unittest.begin(ctx)

    # Empty input
    asserts.equals(env, [], extract_msvc_include_paths(ctx, env = {}, cmd = []))

    # Standard case
    asserts.equals(
        env,
        ["relevant/a", "relevant/a/aa", "relevant/b", "relevant/c"],
        extract_msvc_include_paths(
            ctx,
            env = {"INCLUDE": "relevant/a" + ctx.configuration.host_path_separator + "relevant/a/aa", "UNRELATED": "path/u"},
            cmd = ["/I", "relevant/b", "unrelated", "/I", "relevant/c"],
        ),
    )

    # No duplicate results
    asserts.equals(
        env,
        ["relevant/a", "relevant/b"],
        extract_msvc_include_paths(
            ctx,
            env = {"INCLUDE": "relevant/a" + ctx.configuration.host_path_separator + "relevant/a"},
            cmd = ["/I", "relevant/b", "/I", "relevant/b"],
        ),
    )

    # Edge case yields empty result
    asserts.equals(env, [], extract_msvc_include_paths(ctx, env = {}, cmd = ["/I"]))

    return unittest.end(env)

_extract_msvc_include_paths_test = unittest.make(_extract_msvc_include_paths_test_impl)

def gather_cc_toolchain_headers_test_suite(name):
    unittest.suite(name, _extract_msvc_include_paths_test)
