from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        We move all valid usages into a single test to save time. It does not help us to execute them individually.
        """
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target=["//cc_toolchain_preprocessor:use_extern_valid"],
            aspect="//cc_toolchain_preprocessor:aspect.bzl%dwyu",
        )

        return self._check_result(actual=actual, expected=expected)
