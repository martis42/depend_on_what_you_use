from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        Test that we resolved boost::wave bug https://github.com/boostorg/wave/issues/243 in DWYU.
        """
        actual = self._run_dwyu(target="//files_named_like_folders:all", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=ExpectedSuccess())
