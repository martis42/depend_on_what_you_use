from pathlib import Path

from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(
            success=False,
            invalid_includes=[f"File='{Path('alias/use_a_and_b.cpp')}', include='alias/a.h'"],
        )
        actual = self._run_dwyu(target="//alias:use_a_transitively", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
