load("@bazel_skylib//lib:unittest.bzl", "asserts", "unittest")
load("//dwyu/private:utils.bzl", "label_to_name", "string_to_bool", "unique_list")

def _label_to_name_test_impl(ctx):
    env = unittest.begin(ctx)

    # No changes
    asserts.equals(env, "some_unchanged_string", label_to_name("some_unchanged_string"))

    # Replace characters which are not valid for file names
    asserts.equals(env, "foo_some_path_to_a_target", label_to_name("@foo//some/path/to/a:target"))

    return unittest.end(env)

label_to_name_test = unittest.make(_label_to_name_test_impl)

def _unique_list_test_impl(ctx):
    env = unittest.begin(ctx)

    # Disjoint lists are simply combined
    asserts.equals(env, [1, 2, 3, 4], unique_list([1, 2], [3, 4]))

    # Duplicates within the combined result are removed, first occurrence is kept
    asserts.equals(env, [1, 2, 3], unique_list([1, 2], [2, 3]))

    # Duplicates spanning both lists are removed
    asserts.equals(env, [1, 2, 3], unique_list([1, 2, 3], [1, 2, 3]))

    # Empty inputs
    asserts.equals(env, [], unique_list([], []))
    asserts.equals(env, [1, 2], unique_list([1, 2], []))
    asserts.equals(env, [1, 2], unique_list([], [1, 2]))

    return unittest.end(env)

unique_list_test = unittest.make(_unique_list_test_impl)

def _string_to_bool_test_impl(ctx):
    env = unittest.begin(ctx)

    # Truthy values
    asserts.equals(env, True, string_to_bool("true"))
    asserts.equals(env, True, string_to_bool("1"))
    asserts.equals(env, True, string_to_bool("yes"))

    # Falsy values
    asserts.equals(env, False, string_to_bool("false"))
    asserts.equals(env, False, string_to_bool("0"))
    asserts.equals(env, False, string_to_bool("no"))

    # Case-insensitive
    asserts.equals(env, True, string_to_bool("True"))
    asserts.equals(env, True, string_to_bool("TRUE"))
    asserts.equals(env, False, string_to_bool("False"))
    asserts.equals(env, False, string_to_bool("FALSE"))

    return unittest.end(env)

string_to_bool_test = unittest.make(_string_to_bool_test_impl)

def utils_test_suite(name):
    unittest.suite(
        name,
        label_to_name_test,
        string_to_bool_test,
        unique_list_test,
    )
