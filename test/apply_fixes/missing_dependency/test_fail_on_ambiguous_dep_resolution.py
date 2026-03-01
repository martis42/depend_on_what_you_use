from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//missing_dependency/workspace:use_ambiguous_lib"

    def execute_test_logic(self) -> Result:
        self._create_reports(aspect="//missing_dependency/workspace:aspect.bzl%default_aspect")

        process = self._run_and_capture_cmd(
            cmd=[
                self._bazel_bin,
                "run",
                "@depend_on_what_you_use//:apply_fixes",
                "--",
                f"--dwyu-log-file={self._log_file}",
                "--use-bazel-info",
                "--fix-missing-deps",
            ],
            check=True,
        )

        expected_error = [
            "Found multiple targets providing invalid include path 'missing_dependency/workspace/ambiguous_lib/lib.h'",
            "//missing_dependency/workspace/ambiguous_lib:lib_a",
            "//missing_dependency/workspace/ambiguous_lib:lib_b",
        ]
        if all(msg in process.stderr for msg in expected_error):
            return Success()
        return self._make_unexpected_output_error(expected="\n".join(expected_error), output=process.stderr)
