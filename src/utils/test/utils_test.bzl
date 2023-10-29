load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")
load("//src/utils:utils.bzl", "label_to_name")

def _label_to_name_test_impl(ctx):
    env = unittest.begin(ctx)

    # No changes
    asserts.equals(env, "some_unchanged_string", label_to_name("some_unchanged_string"))

    # Replace characters which are not valid inf ile names
    asserts.equals(env, "foo_some_path_to_a_target", label_to_name("@foo//some/path/to/a:target"))

    return unittest.end(env)

label_to_name_test = unittest.make(_label_to_name_test_impl)

def utils_test_suite(name):
    unittest.suite(
        name,
        label_to_name_test,
    )
