from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Error, Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:binary"

    def execute_test_logic(self) -> Result:
        self._create_reports()

        process = self._run_and_capture_cmd(
            cmd=[
                self._bazel_bin,
                "run",
                "@depend_on_what_you_use//:apply_fixes",
                "--",
                f"--workspace={self._workspace}",
            ],
            check=False,
        )
        if process.returncode == 0:
            return Error("Expected an exception, but none occurred")
        if (expected_error := "Please choose at least one of the 'fix-..' options") not in process.stderr:
            return self._make_unexpected_output_error(expected=expected_error, output=process.stderr)

        return Success()
