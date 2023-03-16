from result import Error, Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:binary"

    def execute_test_logic(self) -> Result:
        self._create_reports()

        process = self._run_and_capture_cmd(
            cmd=["bazel", "run", "@depend_on_what_you_use//:apply_fixes", "--", f"--workspace={self._workspace}"],
            check=False,
        )
        if process.returncode == 0:
            return Error(f"Expected an exception, but none occurred")
        if "Please choose at least of onf the 'fix-..' options" not in process.stderr:
            return Error("Unexpected error output:\n" + process.stderr)

        return Success()
