from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//no_preprocessor:use_libs",
            aspect=self.choose_aspect("//no_preprocessor:aspect.bzl%dwyu_no_preprocessor"),
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
