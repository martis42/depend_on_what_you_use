from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    @property
    def compatible_to_cc_toolchain_based(self) -> bool:
        """
        This is a deprecated feature we will not support with the new CC toolchain based approach.
        Using the preprocessor from the real toolchain should resolve all issues we tried to fix with this experimental feature.
        """
        return False

    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(target="//set_cpp_standard:all", aspect="//set_cpp_standard:aspect.bzl%set_cplusplus")

        return self._check_result(actual=actual, expected=expected)
