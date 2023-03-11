from result import Error, Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:use_private_header"

    def execute_test_logic(self) -> Result:
        self._create_reports()
        self._run_automatic_fix(extra_args=["--fix-missing-deps"])

        process = self._run_and_capture_cmd(
            cmd=[
                "bazel",
                "run",
                "@depend_on_what_you_use//:apply_fixes",
                "--",
                "--fix-missing-deps",
                f"--workspace={self._workspace}",
            ],
            check=True,
        )

        if "Could not find a proper dependency for invalid include 'bar/private_bar.h'" in process.stderr:
            return Success()
        else:
            return Error(f"Did not see the expected error. Unexpected stderr:\n{process.stderr}")
