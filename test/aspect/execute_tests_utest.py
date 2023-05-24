import unittest
from shutil import which

from execute_tests_impl import (
    CATEGORY_INVALID_INCLUDES,
    CATEGORY_NON_PRIVATE_DEPS,
    CATEGORY_UNUSED_PRIVATE_DEPS,
    CATEGORY_UNUSED_PUBLIC_DEPS,
    DWYU_FAILURE,
    ERRORS_PREFIX,
    CompatibleVersions,
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
        for cat in [CATEGORY_NON_PRIVATE_DEPS, CATEGORY_UNUSED_PUBLIC_DEPS, CATEGORY_UNUSED_PRIVATE_DEPS]:
            self.assertFalse(
                unit.matches_expectation(
                    return_code=1,
                    dwyu_output=self._make_error_output(category=cat, errors=["foo/bar.cpp", "bar/foo.h"]),
                )
            )

    def test_expected_fail_due_to_unused_public_deps(self):
        unit = ExpectedResult(success=False, unused_public_deps=["//foo:bar", "//bar:foo"])
        self.assertTrue(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(
                    category=CATEGORY_UNUSED_PUBLIC_DEPS, errors=["//foo:bar", "//bar:foo"]
                ),
            )
        )

    def test_expected_fail_due_to_unused_public_deps_fails(self):
        unit = ExpectedResult(success=False, unused_public_deps=["//foo:bar", "//bar:foo"])
        self.assertFalse(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_UNUSED_PUBLIC_DEPS, errors=["//foo:bar"]),
            )
        )

    def test_expected_fail_due_to_unused_public_deps_fails_on_other_error(self):
        unit = ExpectedResult(success=False, unused_public_deps=["//foo:bar", "//bar:foo"])
        for cat in [CATEGORY_INVALID_INCLUDES, CATEGORY_NON_PRIVATE_DEPS, CATEGORY_UNUSED_PRIVATE_DEPS]:
            self.assertFalse(
                unit.matches_expectation(
                    return_code=1,
                    dwyu_output=self._make_error_output(category=cat, errors=["//foo:bar", "//bar:foo"]),
                )
            )

    def test_expected_fail_due_to_unused_private_deps(self):
        unit = ExpectedResult(success=False, unused_private_deps=["//foo:bar", "//bar:foo"])
        self.assertTrue(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(
                    category=CATEGORY_UNUSED_PRIVATE_DEPS, errors=["//foo:bar", "//bar:foo"]
                ),
            )
        )

    def test_expected_fail_due_to_unused_private_deps_fails(self):
        unit = ExpectedResult(success=False, unused_private_deps=["//foo:bar", "//bar:foo"])
        self.assertFalse(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_UNUSED_PRIVATE_DEPS, errors=["//foo:bar"]),
            )
        )

    def test_expected_fail_due_to_unused_private_deps_fails_on_other_error(self):
        unit = ExpectedResult(success=False, unused_private_deps=["//foo:bar", "//bar:foo"])
        for cat in [CATEGORY_INVALID_INCLUDES, CATEGORY_NON_PRIVATE_DEPS, CATEGORY_UNUSED_PUBLIC_DEPS]:
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
        for cat in [CATEGORY_INVALID_INCLUDES, CATEGORY_UNUSED_PUBLIC_DEPS, CATEGORY_UNUSED_PRIVATE_DEPS]:
            self.assertFalse(
                unit.matches_expectation(
                    return_code=1,
                    dwyu_output=self._make_error_output(category=cat, errors=["//foo:bar", "//bar:foo"]),
                )
            )


class TestMakeCmd(unittest.TestCase):
    @staticmethod
    def _base_cmd(startup_args=None):
        bazel = which("bazelisk") or which("bazel")
        build_with_default_options = ["build", "--noshow_progress"]
        if startup_args:
            return [bazel] + startup_args + build_with_default_options
        return [bazel] + build_with_default_options

    def test_basic_cmd(self):
        cmd = make_cmd(test_cmd=TestCmd(target="//foo:bar"), extra_args=[], startup_args=[])
        self.assertEqual(cmd, self._base_cmd() + ["--", "//foo:bar"])

    def test_complex_test_cmd(self):
        cmd = make_cmd(
            test_cmd=TestCmd(
                target="//foo:bar",
                aspect="//some/aspect.bzl",
                extra_args=["--abc", "--cba"],
            ),
            extra_args=[],
            startup_args=[],
        )
        self.assertEqual(
            cmd,
            self._base_cmd()
            + ["--aspects=//some/aspect.bzl", "--output_groups=cc_dwyu_output", "--abc", "--cba", "--", "//foo:bar"],
        )

    def test_extra_args_on_top_of_test_cmd(self):
        cmd = make_cmd(
            test_cmd=TestCmd(
                target="//foo:bar",
                aspect="//some/aspect.bzl",
                extra_args=["--test_related_arg"],
            ),
            extra_args=["--outside_arg"],
            startup_args=["--some_startup_arg"],
        )
        self.assertEqual(
            cmd,
            self._base_cmd(startup_args=["--some_startup_arg"])
            + [
                "--aspects=//some/aspect.bzl",
                "--output_groups=cc_dwyu_output",
                "--outside_arg",
                "--test_related_arg",
                "--",
                "//foo:bar",
            ],
        )


class TestIsCompatibleVersion(unittest.TestCase):
    def test_no_limits(self):
        self.assertTrue(CompatibleVersions().is_compatible_to("1.0.0"))

    def test_above_min_version(self):
        self.assertTrue(CompatibleVersions(min="0.9.9").is_compatible_to("1.0.0"))

    def test_below_min_version(self):
        self.assertFalse(CompatibleVersions(min="1.1.9").is_compatible_to("1.0.0"))

    def test_below_max_version(self):
        self.assertTrue(CompatibleVersions(max="1.1.0").is_compatible_to("1.0.0"))

    def test_above_max_version(self):
        self.assertFalse(CompatibleVersions(max="0.9.0").is_compatible_to("1.0.0"))

    def test_inside_interval(self):
        self.assertTrue(CompatibleVersions(min="0.9.0", max="1.1.0").is_compatible_to("1.0.0"))


if __name__ == "__main__":
    unittest.main()
