from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        A test listening to the output group 'dwyu_check' should behave like listening to the default output group 'dwyu'.
        """
        target = "//output_groups:main"
        actual = self._run_dwyu(target=target, aspect=self.default_aspect, output_group="dwyu_check")
        expected = ExpectedFailure(ExpectedDwyuFailure(target=target, unused_public_deps=["//output_groups:unused"]))
        return self._check_result(actual=actual, expected=expected)
