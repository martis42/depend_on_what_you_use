from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(
            success=False,
            invalid_includes=["File='alias/use_a_and_b.cpp', include='alias/a.h'"],
        )
        actual = self._run_dwyu(target="//alias:use_a_transitively", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
