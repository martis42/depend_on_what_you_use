from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        Test that files with the same basename in different packages are handled correctly.
        """

        actual = self._run_dwyu(
            target=["//files_with_same_name:all", "@files_with_same_name_test_repo//:all"], aspect=self.default_aspect
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
