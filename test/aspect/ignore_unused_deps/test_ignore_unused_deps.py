from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//ignore_unused_deps:lib_with_unused_deps",
            aspect=self.choose_aspect("//ignore_unused_deps:aspect.bzl%dwyu_ignore_unused_deps"),
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
