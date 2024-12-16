from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, unused_public_deps=["//unused_dep:foo"])
        actual = self._run_dwyu(target="//unused_dep:main", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
