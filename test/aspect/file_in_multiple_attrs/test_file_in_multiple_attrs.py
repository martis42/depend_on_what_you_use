from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        Show that the aspect handles a file appearing in both hdrs and srcs of the same target.
        """
        actual = self._run_dwyu(target="//file_in_multiple_attrs:lib", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=ExpectedSuccess())
