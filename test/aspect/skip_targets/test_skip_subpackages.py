from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target=["//skip_targets/sub:broken_a", "//skip_targets/sub/nested:broken_nested"],
            aspect=self.choose_aspect("//skip_targets:aspect.bzl%dwyu_skip_recursive_pattern"),
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
