from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, unused_public_deps=["//recursion:e"])
        actual = self._run_dwyu(
            target="//recursion:use_impl_deps", aspect=self.choose_aspect("//recursion:aspect.bzl%dwyu_recursive")
        )

        return self._check_result(actual=actual, expected=expected)
