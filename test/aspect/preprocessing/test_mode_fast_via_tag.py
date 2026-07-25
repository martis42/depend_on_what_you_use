from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//preprocessing/fast:no_preprocessing_with_preprocessing_chosen_by_tag", aspect=self.default_aspect
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
