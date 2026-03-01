from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//missing_dependency/workspace:use_invisible_lib"

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

        expected_error = "Could not find a proper dependency for invalid include path 'missing_dependency/workspace/libs/private.h' of target '@@//missing_dependency/workspace:use_invisible_lib'"
        if expected_error in process.stderr:
            return Success()
        return self._make_unexpected_output_error(expected=expected_error, output=process.stderr)
