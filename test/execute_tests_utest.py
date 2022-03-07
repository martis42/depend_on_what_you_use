import unittest

from execute_tests_impl import (
    CATEGORY_INVALID_INCLUDES,
    CATEGORY_NON_PRIVATE_DEPS,
    CATEGORY_UNUSED_DEPS,
    CATEGORY_UTILIZATION,
    DWYU_FAILURE,
    ERRORS_PREFIX,
    ExpectedResult,
    TestCmd,
    make_cmd,
)


class TestExpectedResult(unittest.TestCase):
    @staticmethod
    def _make_error_output(category, errors):
        msg = DWYU_FAILURE + "\n"
        msg += category + "\n"
        msg += "\n".join(f"{ERRORS_PREFIX}{err}" for err in errors)
        return msg

    def test_expected_success_ok(self):
        unit = ExpectedResult(success=True)
        self.assertTrue(unit.matches_expectation(return_code=0, dwyu_output=""))

    def test_expected_success_error(self):
        unit = ExpectedResult(success=True)
        self.assertFalse(unit.matches_expectation(return_code=1, dwyu_output=""))

    def test_expected_failure_ok(self):
        unit = ExpectedResult(success=False)
        self.assertTrue(unit.matches_expectation(return_code=1, dwyu_output=DWYU_FAILURE))

    def test_expected_failure_error(self):
        unit = ExpectedResult(success=False)
        self.assertFalse(unit.matches_expectation(return_code=0, dwyu_output=""))

    def test_expected_failure_error_due_to_missing_output(self):
        unit = ExpectedResult(success=False)
        self.assertFalse(unit.matches_expectation(return_code=1, dwyu_output=""))

    def test_expected_fail_due_to_invalid_includes(self):
        unit = ExpectedResult(success=False, invalid_includes=["foo/bar.cpp", "bar/foo.h"])
        self.assertTrue(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(
                    category=CATEGORY_INVALID_INCLUDES, errors=["foo/bar.cpp", "bar/foo.h"]
                ),
            )
        )

    def test_expected_fail_due_to_invalid_includes_fails(self):
        unit = ExpectedResult(success=False, invalid_includes=["foo/bar.cpp", "bar/foo.h"])
        self.assertFalse(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_INVALID_INCLUDES, errors=["foo/bar.cpp"]),
            )
        )

    def test_expected_fail_due_to_invalid_includes_fails_on_other_error(self):
        unit = ExpectedResult(success=False, invalid_includes=["foo/bar.cpp", "bar/foo.h"])
        for cat in [CATEGORY_NON_PRIVATE_DEPS, CATEGORY_UNUSED_DEPS, CATEGORY_UTILIZATION]:
            self.assertFalse(
                unit.matches_expectation(
                    return_code=1,
                    dwyu_output=self._make_error_output(category=cat, errors=["foo/bar.cpp", "bar/foo.h"]),
                )
            )

    def test_expected_fail_due_to_unused_deps(self):
        unit = ExpectedResult(success=False, unused_deps=["//foo:bar", "//bar:foo"])
        self.assertTrue(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_UNUSED_DEPS, errors=["//foo:bar", "//bar:foo"]),
            )
        )

    def test_expected_fail_due_to_unused_deps_fails(self):
        unit = ExpectedResult(success=False, unused_deps=["//foo:bar", "//bar:foo"])
        self.assertFalse(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_UNUSED_DEPS, errors=["//foo:bar"]),
            )
        )

    def test_expected_fail_due_to_unused_deps_fails_on_other_error(self):
        unit = ExpectedResult(success=False, unused_deps=["//foo:bar", "//bar:foo"])
        for cat in [CATEGORY_INVALID_INCLUDES, CATEGORY_NON_PRIVATE_DEPS, CATEGORY_UTILIZATION]:
            self.assertFalse(
                unit.matches_expectation(
                    return_code=1,
                    dwyu_output=self._make_error_output(category=cat, errors=["//foo:bar", "//bar:foo"]),
                )
            )

    def test_expected_fail_due_to_non_private_deps(self):
        unit = ExpectedResult(success=False, deps_which_should_be_private=["//foo:bar", "//bar:foo"])
        self.assertTrue(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(
                    category=CATEGORY_NON_PRIVATE_DEPS, errors=["//foo:bar", "//bar:foo"]
                ),
            )
        )

    def test_expected_fail_due_to_non_private_deps_fails(self):
        unit = ExpectedResult(success=False, deps_which_should_be_private=["//foo:bar", "//bar:foo"])
        self.assertFalse(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_NON_PRIVATE_DEPS, errors=["//foo:bar"]),
            )
        )

    def test_expected_fail_due_to_non_private_deps_fails_on_other_error(self):
        unit = ExpectedResult(success=False, deps_which_should_be_private=["//foo:bar", "//bar:foo"])
        for cat in [CATEGORY_INVALID_INCLUDES, CATEGORY_UNUSED_DEPS, CATEGORY_UTILIZATION]:
            self.assertFalse(
                unit.matches_expectation(
                    return_code=1,
                    dwyu_output=self._make_error_output(category=cat, errors=["//foo:bar", "//bar:foo"]),
                )
            )

    def test_expected_fail_due_to_low_utilization(self):
        unit = ExpectedResult(success=False, deps_with_low_utilization=["//foo:bar", "//bar:foo"])
        self.assertTrue(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_UTILIZATION, errors=["//foo:bar", "//bar:foo"]),
            )
        )

    def test_expected_fail_due_to_low_utilization_fails(self):
        unit = ExpectedResult(success=False, deps_with_low_utilization=["//foo:bar", "//bar:foo"])
        self.assertFalse(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_UTILIZATION, errors=["//foo:bar"]),
            )
        )

    def test_expected_fail_due_to_low_utilization_on_other_error(self):
        unit = ExpectedResult(success=False, deps_with_low_utilization=["//foo:bar", "//bar:foo"])
        for cat in [CATEGORY_INVALID_INCLUDES, CATEGORY_NON_PRIVATE_DEPS, CATEGORY_UNUSED_DEPS]:
            self.assertFalse(
                unit.matches_expectation(
                    return_code=1,
                    dwyu_output=self._make_error_output(category=cat, errors=["//foo:bar", "//bar:foo"]),
                )
            )


class TestMakeCmd(unittest.TestCase):
    @staticmethod
    def _base_cmd():
        return ["bazelisk", "build", "--noshow_progress"]

    def test_with_aspect(self):
        cmd = make_cmd(test_cmd=TestCmd(target="//foo:bar"), extra_args=[])
        self.assertEqual(cmd, self._base_cmd() + ["--", "//foo:bar"])

    def test_with_aspect(self):
        cmd = make_cmd(test_cmd=TestCmd(target="//foo:bar", aspect="//some/aspect.bzl"), extra_args=[])
        self.assertEqual(
            cmd,
            self._base_cmd() + ["--aspects=//some/aspect.bzl", "--output_groups=cc_dwyu_output", "--", "//foo:bar"],
        )

    def test_with_extra_args(self):
        cmd = make_cmd(
            test_cmd=TestCmd(target="//foo:bar", extra_args=["--abc", "--cba"]), extra_args=["--some_bazel_extra_arg"]
        )
        self.assertEqual(cmd, self._base_cmd() + ["--some_bazel_extra_arg", "--abc", "--cba", "--", "//foo:bar"])


if __name__ == "__main__":
    unittest.main()
