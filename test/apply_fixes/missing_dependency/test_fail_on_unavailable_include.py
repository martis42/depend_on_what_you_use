from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:use_private_header"

    def execute_test_logic(self) -> Result:
        self._create_reports()
        self._run_automatic_fix(extra_args=["--fix-missing-deps"])

        process = self._run_and_capture_cmd(
            cmd=[
                self._bazel_bin,
                "run",
                "@depend_on_what_you_use//:apply_fixes",
                "--",
                "--fix-missing-deps",
                f"--workspace={self._workspace}",
            ],
            check=True,
        )

        expected_error = "Could not find a proper dependency for invalid include path 'private_header/private_bar.h'"
        if expected_error not in process.stderr:
            return self._make_unexpected_output_error(expected=expected_error, output=process.stderr)
        return Success()
