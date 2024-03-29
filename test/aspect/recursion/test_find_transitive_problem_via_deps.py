from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, unused_public_deps=["//recursion:e"])
        actual = self._run_dwyu(target="//recursion:main", aspect="//recursion:aspect.bzl%dwyu_recursive")

        return self._check_result(actual=actual, expected=expected)
