from platform import system

from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


def make_define(flag: str) -> str:
    """
    MVSC on Windows has another syntax than gcc and clang
    """
    control_character = "/" if system() == "Windows" else "-"
    return f"{control_character}D{flag}"


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//defines:use_command_line_defines",
            aspect=self.default_aspect,
            extra_args=[f"--cxxopt={make_define('SOME_FLAG')}", f"--cxxopt={make_define('SOME_VALUE=42')}"],
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
