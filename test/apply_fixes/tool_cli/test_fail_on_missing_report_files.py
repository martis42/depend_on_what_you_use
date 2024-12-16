from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Error, Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:binary"

    def execute_test_logic(self) -> Result:
        # Don't create report files to trigger a failure by the apply_fixes script.

        process = self._run_and_capture_cmd(
            cmd=[
                self._bazel_bin,
                "run",
                "@depend_on_what_you_use//:apply_fixes",
                "--",
                f"--workspace={self._workspace}",
                "--fix-all",
            ],
            check=False,
        )

        if process.returncode == 0:
            return Error("Expected an exception, but none occurred")
        if (expected_error := "ERROR: Did not find any DWYU report files.") not in process.stderr:
            return self._make_unexpected_output_error(expected=expected_error, output=process.stderr)

        return Success()
