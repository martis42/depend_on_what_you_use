from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        Working in external repositories has its own challenges due to some paths behaving different compared to
        working inside the own workspace. Thus, we explicitly test working in an external workspace on top of normal
        targets from within the main workspace.
        """
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target=["//complex_includes:all", "@complex_includes_test_repo//..."],
            aspect=self.default_aspect,
        )

        return self._check_result(actual=actual, expected=expected)
