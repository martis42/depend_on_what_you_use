from __future__ import annotations

from dataclasses import dataclass, field

# Each line in the output corresponding to an error is expected to start with this
ERRORS_PREFIX = " " * 2

# DWYU terminal output key fragments
DWYU_FAILURE = "Result: FAILURE"
CATEGORY_INVALID_INCLUDES = "Includes which are not available from the direct dependencies"
CATEGORY_NON_PRIVATE_DEPS = "deps' which should be moved to 'implementation_deps'"
CATEGORY_NON_PRIVATE_DEPS_LEGACY = "Public dependencies which are used only in private code"
CATEGORY_UNUSED_PUBLIC_DEPS = "Unused dependencies in 'deps'"
CATEGORY_UNUSED_PRIVATE_DEPS = "Unused dependencies in 'implementation_deps'"


@dataclass
class ExpectedResult:
    """
    Encapsulates an expected result of a DWYU analysis and offers functions
    to compare a given output to the expectations.
    """

    success: bool
    invalid_includes: list[str] = field(default_factory=list)
    unused_public_deps: list[str] = field(default_factory=list)
    unused_private_deps: list[str] = field(default_factory=list)
    deps_which_should_be_private: list[str] = field(default_factory=list)

    def matches_expectation(self, return_code: int, dwyu_output: str, is_cpp_impl: bool) -> bool:
        if not self._has_correct_status(return_code=return_code, output=dwyu_output):
            return False

        output_lines = dwyu_output.split("\n")
        if not ExpectedResult._has_expected_errors(
            expected_errors=self.invalid_includes,
            error_category=CATEGORY_INVALID_INCLUDES,
            output=output_lines,
        ):
            return False
        if not ExpectedResult._has_expected_errors(
            expected_errors=self.unused_public_deps,
            error_category=CATEGORY_UNUSED_PUBLIC_DEPS,
            output=output_lines,
        ):
            return False
        if not ExpectedResult._has_expected_errors(
            expected_errors=self.unused_private_deps,
            error_category=CATEGORY_UNUSED_PRIVATE_DEPS,
            output=output_lines,
        ):
            return False
        if not ExpectedResult._has_expected_errors(  # noqa: SIM103
            expected_errors=self.deps_which_should_be_private,
            error_category=CATEGORY_NON_PRIVATE_DEPS if is_cpp_impl else CATEGORY_NON_PRIVATE_DEPS_LEGACY,
            output=output_lines,
        ):
            return False

        return True

    def _has_correct_status(self, return_code: int, output: str) -> bool:
        if self.success and return_code == 0:
            return True
        return not self.success and return_code != 0 and DWYU_FAILURE in output

    @staticmethod
    def _get_error_lines(idx_category: int, output: list[str]) -> list[str]:
        errors_begin = idx_category + 1
        errors_end = 0
        for i in range(errors_begin, len(output)):
            if output[i].startswith(ERRORS_PREFIX):
                errors_end = i + 1
            else:
                break
        return output[errors_begin:errors_end]

    @staticmethod
    def _has_expected_errors(expected_errors: list[str], error_category: str, output: list[str]) -> bool:
        if not expected_errors:
            return True

        idx_category = ExpectedResult._find_line_with(lines=output, val=error_category)
        if idx_category is None:
            return False

        return ExpectedResult._has_errors(
            error_lines=ExpectedResult._get_error_lines(idx_category=idx_category, output=output),
            expected_errors=expected_errors,
        )

    @staticmethod
    def _find_line_with(lines: list[str], val: str) -> int | None:
        for idx, line in enumerate(lines):
            if val in line:
                return idx
        return None

    @staticmethod
    def _has_errors(error_lines: list[str], expected_errors: list[str]) -> bool:
        if len(error_lines) != len(expected_errors):
            return False
        return all(any(error in line for line in error_lines) for error in expected_errors)
