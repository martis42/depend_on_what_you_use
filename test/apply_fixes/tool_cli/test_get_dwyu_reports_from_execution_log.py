from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//tool_cli/workspace/..."

    def execute_test_logic(self) -> Result:
        """
        This test is a noop since the whole test setup is based on capturing and passing a log file with the DWYU output.
        We just keep this file to document we did not forget about this prt of the CLI.
        """
        return Success()
