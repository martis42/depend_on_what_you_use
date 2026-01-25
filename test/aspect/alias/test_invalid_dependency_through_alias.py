from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//alias:use_a_transitively"
        expected = ExpectedFailure(
            ExpectedDwyuFailure(target=target, invalid_includes={"alias/use_a_and_b.cpp": ["alias/a.h"]})
        )
        actual = self._run_dwyu(target=target, aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
