from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//set_cpp_standard:all", aspect=self.choose_aspect("//set_cpp_standard:aspect.bzl%set_cplusplus")
        )

        return self._check_result(actual=actual, expected=expected)
