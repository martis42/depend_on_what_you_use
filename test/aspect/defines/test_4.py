from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(target="//defines:use_defines_from_dependency_header", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
