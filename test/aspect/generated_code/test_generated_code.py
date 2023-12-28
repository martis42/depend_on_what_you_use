from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        Show that the aspect properly processes generated code which lives only in the bazel output tree.
        """
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(target="//test/aspect/generated_code:foo", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
