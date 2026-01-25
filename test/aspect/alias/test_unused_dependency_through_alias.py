from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//alias:unused_dependency"
        expected = ExpectedFailure(ExpectedDwyuFailure(target=target, unused_public_deps=["//alias:lib_a"]))
        actual = self._run_dwyu(target=target, aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
