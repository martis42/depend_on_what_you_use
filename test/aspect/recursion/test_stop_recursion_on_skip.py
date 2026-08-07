from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    """
    Unless we skip '//recursion:a' and '//recursion:b' and abort the recursion there, we would reach '//recursion:c' and fail there due to its unused dependency
    """

    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//recursion:main", aspect=self.choose_aspect("//recursion:aspect.bzl%dwyu_recursive_stop_on_skip")
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
