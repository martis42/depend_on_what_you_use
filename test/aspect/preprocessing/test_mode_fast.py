from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//preprocessing/fast:no_preprocessing", aspect="//preprocessing:aspect.bzl%dwyu_fast"
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
