from result import Error, Result, Success
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
                "bazel",
                "run",
                "@depend_on_what_you_use//:apply_fixes",
                "--",
                "--fix-missing-deps",
                f"--workspace={self._workspace}",
            ],
            check=True,
        )

        if all(
            msg in process.stderr
            for msg in (
                "Found multiple targets which potentially can provide include 'ambiguous_lib/lib.h'",
                "//ambiguous_lib:lib_a",
                "//ambiguous_lib:lib_b",
            )
        ):
            return Success()
        else:
            return Error(f"Did not see the expected error. Unexpected stderr:\n{process.stderr}")
