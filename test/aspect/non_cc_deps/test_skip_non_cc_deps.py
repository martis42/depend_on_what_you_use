from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(target="//non_cc_deps:lib_with_non_cc_deps", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=ExpectedSuccess())
