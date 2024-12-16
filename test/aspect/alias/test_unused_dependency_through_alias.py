from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, unused_public_deps=["//alias:lib_a"])
        actual = self._run_dwyu(target="//alias:unused_dependency", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
