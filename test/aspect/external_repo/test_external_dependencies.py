from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        Working with external repositories has its own challenges due to some paths behaving different compared to
        working inside the own workspace. This test shows DWYU can be invoked on targets using libraries from external
        workspaces without failing unexpectedly.
        """
        actual = self._run_dwyu(target="//external_repo:use_external_libs", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=ExpectedSuccess())
