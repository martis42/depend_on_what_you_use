from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        Show that the aspect properly processes generated code which lives only in the bazel output tree.
        """
        actual = self._run_dwyu(target="//generated_code:foo", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=ExpectedSuccess())
