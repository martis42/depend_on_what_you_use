from __future__ import annotations

import unittest

from expected_result import (
    CATEGORY_INVALID_INCLUDES,
    CATEGORY_NON_PRIVATE_DEPS,
    CATEGORY_UNUSED_PRIVATE_DEPS,
    CATEGORY_UNUSED_PUBLIC_DEPS,
    DWYU_FAILURE,
    ERRORS_PREFIX,
    ExpectedResult,
)

from test.support.result import Error, Success


class TestExpectedResult(unittest.TestCase):
    @staticmethod
    def _make_error_output(category: str, errors: list[str]) -> str:
        msg = DWYU_FAILURE + "\n"
        msg += category + "\n"
        msg += "\n".join(f"{ERRORS_PREFIX}{err}" for err in errors)
        return msg

    def test_expected_success_ok(self) -> None:
        unit = ExpectedResult(success=True)
        self.assertTrue(unit.matches_expectation(return_code=0, dwyu_output=""))

    def test_expected_success_error(self) -> None:
        unit = ExpectedResult(success=True)
        self.assertFalse(unit.matches_expectation(return_code=1, dwyu_output=""))

    def test_expected_failure_ok(self) -> None:
        unit = ExpectedResult(success=False)
        self.assertTrue(unit.matches_expectation(return_code=1, dwyu_output=DWYU_FAILURE))

    def test_expected_failure_error(self) -> None:
        unit = ExpectedResult(success=False)
        self.assertFalse(unit.matches_expectation(return_code=0, dwyu_output=""))

    def test_expected_failure_error_due_to_missing_output(self) -> None:
        unit = ExpectedResult(success=False)
        self.assertFalse(unit.matches_expectation(return_code=1, dwyu_output=""))

    def test_expected_fail_due_to_invalid_includes(self) -> None:
        unit = ExpectedResult(success=False, invalid_includes=["foo/bar.cpp", "bar/foo.h"])
        self.assertTrue(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(
                    category=CATEGORY_INVALID_INCLUDES, errors=["foo/bar.cpp", "bar/foo.h"]
                ),
            )
        )

    def test_expected_fail_due_to_invalid_includes_fails(self) -> None:
        unit = ExpectedResult(success=False, invalid_includes=["foo/bar.cpp", "bar/foo.h"])
        self.assertFalse(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_INVALID_INCLUDES, errors=["foo/bar.cpp"]),
            )
        )

    def test_expected_fail_due_to_invalid_includes_fails_on_other_error(self) -> None:
        unit = ExpectedResult(success=False, invalid_includes=["foo/bar.cpp", "bar/foo.h"])
        for cat in [CATEGORY_NON_PRIVATE_DEPS, CATEGORY_UNUSED_PUBLIC_DEPS, CATEGORY_UNUSED_PRIVATE_DEPS]:
            self.assertFalse(
                unit.matches_expectation(
                    return_code=1,
                    dwyu_output=self._make_error_output(category=cat, errors=["foo/bar.cpp", "bar/foo.h"]),
                )
            )

    def test_expected_fail_due_to_unused_public_deps(self) -> None:
        unit = ExpectedResult(success=False, unused_public_deps=["//foo:bar", "//bar:foo"])
        self.assertTrue(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(
                    category=CATEGORY_UNUSED_PUBLIC_DEPS, errors=["//foo:bar", "//bar:foo"]
                ),
            )
        )

    def test_expected_fail_due_to_unused_public_deps_fails(self) -> None:
        unit = ExpectedResult(success=False, unused_public_deps=["//foo:bar", "//bar:foo"])
        self.assertFalse(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_UNUSED_PUBLIC_DEPS, errors=["//foo:bar"]),
            )
        )

    def test_expected_fail_due_to_unused_public_deps_fails_on_other_error(self) -> None:
        unit = ExpectedResult(success=False, unused_public_deps=["//foo:bar", "//bar:foo"])
        for cat in [CATEGORY_INVALID_INCLUDES, CATEGORY_NON_PRIVATE_DEPS, CATEGORY_UNUSED_PRIVATE_DEPS]:
            self.assertFalse(
                unit.matches_expectation(
                    return_code=1,
                    dwyu_output=self._make_error_output(category=cat, errors=["//foo:bar", "//bar:foo"]),
                )
            )

    def test_expected_fail_due_to_unused_private_deps(self) -> None:
        unit = ExpectedResult(success=False, unused_private_deps=["//foo:bar", "//bar:foo"])
        self.assertTrue(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(
                    category=CATEGORY_UNUSED_PRIVATE_DEPS, errors=["//foo:bar", "//bar:foo"]
                ),
            )
        )

    def test_expected_fail_due_to_unused_private_deps_fails(self) -> None:
        unit = ExpectedResult(success=False, unused_private_deps=["//foo:bar", "//bar:foo"])
        self.assertFalse(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_UNUSED_PRIVATE_DEPS, errors=["//foo:bar"]),
            )
        )

    def test_expected_fail_due_to_unused_private_deps_fails_on_other_error(self) -> None:
        unit = ExpectedResult(success=False, unused_private_deps=["//foo:bar", "//bar:foo"])
        for cat in [CATEGORY_INVALID_INCLUDES, CATEGORY_NON_PRIVATE_DEPS, CATEGORY_UNUSED_PUBLIC_DEPS]:
            self.assertFalse(
                unit.matches_expectation(
                    return_code=1,
                    dwyu_output=self._make_error_output(category=cat, errors=["//foo:bar", "//bar:foo"]),
                )
            )

    def test_expected_fail_due_to_non_private_deps(self) -> None:
        unit = ExpectedResult(success=False, deps_which_should_be_private=["//foo:bar", "//bar:foo"])
        self.assertTrue(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(
                    category=CATEGORY_NON_PRIVATE_DEPS, errors=["//foo:bar", "//bar:foo"]
                ),
            )
        )

    def test_expected_fail_due_to_non_private_deps_fails(self) -> None:
        unit = ExpectedResult(success=False, deps_which_should_be_private=["//foo:bar", "//bar:foo"])
        self.assertFalse(
            unit.matches_expectation(
                return_code=1,
                dwyu_output=self._make_error_output(category=CATEGORY_NON_PRIVATE_DEPS, errors=["//foo:bar"]),
            )
        )

    def test_expected_fail_due_to_non_private_deps_fails_on_other_error(self) -> None:
        unit = ExpectedResult(success=False, deps_which_should_be_private=["//foo:bar", "//bar:foo"])
        for cat in [CATEGORY_INVALID_INCLUDES, CATEGORY_UNUSED_PUBLIC_DEPS, CATEGORY_UNUSED_PRIVATE_DEPS]:
            self.assertFalse(
                unit.matches_expectation(
                    return_code=1,
                    dwyu_output=self._make_error_output(category=cat, errors=["//foo:bar", "//bar:foo"]),
                )
            )


class TestResult(unittest.TestCase):
    def test_success(self) -> None:
        unit = Success()
        self.assertTrue(unit.is_success())
        self.assertEqual(unit.error, "")

    def test_error(self) -> None:
        unit = Error("foo")
        self.assertFalse(unit.is_success())
        self.assertEqual(unit.error, "foo")


if __name__ == "__main__":
    unittest.main()
