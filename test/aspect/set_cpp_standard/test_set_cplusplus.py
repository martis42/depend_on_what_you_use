from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(target="//set_cpp_standard:all", aspect="//set_cpp_standard:aspect.bzl%set_cplusplus")

        return self._check_result(actual=actual, expected=expected)
