from result import Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:use_ambiguous_lib"

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

        expected_error = [
            "Found multiple targets providing invalid include path 'ambiguous_lib/lib.h'",
            "//ambiguous_lib:lib_a",
            "//ambiguous_lib:lib_b",
        ]
        if all(msg in process.stderr for msg in expected_error):
            return Success()
        return self._make_unexpected_output_error(expected="\n".join(expected_error), output=process.stderr)
