from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    @property
    def compatible_to_cc_toolchain_based(self) -> bool:
        """
        Running the preprocessor is right now not abe to pass large amounts of arguments to gcc via a file
        """
        return False

    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(target="//command_length_limit:many_defines", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
