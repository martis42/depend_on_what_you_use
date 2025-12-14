from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(target="//relative_includes:use_virtual_prefix", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
