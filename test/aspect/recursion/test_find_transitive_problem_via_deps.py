from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//recursion:main", aspect=self.choose_aspect("//recursion:aspect.bzl%dwyu_recursive")
        )
        expected = ExpectedFailure(ExpectedDwyuFailure(target="//recursion:c", unused_public_deps=["//recursion:e"]))

        return self._check_result(actual=actual, expected=expected)
