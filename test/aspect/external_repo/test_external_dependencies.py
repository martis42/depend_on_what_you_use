from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        Working with external repositories has its own challenges due to some paths behaving different compared to
        working inside the own workspace. This test shows DWYU can be invoked on targets using libraries from external
        workspaces without failing unexpectedly.
        """
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(target="//test/aspect/external_repo:use_external_libs", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
