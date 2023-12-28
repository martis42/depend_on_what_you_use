from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//test/aspect/skip_tags:ignored_by_default_behavior", aspect=self.default_aspect
        )

        return self._check_result(actual=actual, expected=expected)
