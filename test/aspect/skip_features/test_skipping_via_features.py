from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(target="//skip_features:all", aspect="//skip_features:aspect.bzl%dwyu_skip_features")

        return self._check_result(actual=actual, expected=ExpectedSuccess())
