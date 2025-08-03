from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    @property
    def compatible_to_cc_toolchain_based(self) -> bool:
        """
        Currently not implemented in the new DWYU implementation
        """
        return False

    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//no_preprocessor:use_libs", aspect="//no_preprocessor:aspect.bzl%dwyu_no_preprocessor"
        )

        return self._check_result(actual=actual, expected=expected)
