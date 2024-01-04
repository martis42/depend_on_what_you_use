from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_bazel_build(target="//rule_using_aspect:dwyu_direct_main")

        return self._check_result(actual=actual, expected=expected)
