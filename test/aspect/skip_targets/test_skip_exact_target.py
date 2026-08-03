from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//skip_targets:broken_exact",
            aspect=self.choose_aspect("//skip_targets:aspect.bzl%dwyu_skip_exact"),
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
