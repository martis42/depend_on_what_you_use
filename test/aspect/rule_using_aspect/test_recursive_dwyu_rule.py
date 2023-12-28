from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, unused_public_deps=["//test/aspect/rule_using_aspect:c"])
        actual = self._run_bazel_build(target="//test/aspect/rule_using_aspect:dwyu_recursive_main")

        return self._check_result(actual=actual, expected=expected)
