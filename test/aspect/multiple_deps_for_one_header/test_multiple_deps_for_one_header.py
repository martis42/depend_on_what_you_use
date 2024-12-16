from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        Multiple dependencies providing the same header can be considered an antipattern. Still, with respect to the
        DWYU principles it is not wrong. Such cases should not cause a DWYU error.
        """
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(target="//multiple_deps_for_one_header:foo", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
