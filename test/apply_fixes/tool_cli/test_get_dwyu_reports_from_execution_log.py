from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//..."

    def execute_test_logic(self) -> Result:
        dwyu_cmd = self._make_create_reports_cmd(extra_args=["--keep_going"])
        dwyu_process = self._run_and_capture_cmd(dwyu_cmd, check=False)

        log_file = self._workspace / "dwyu_log.log"
        log_file.write_text(dwyu_process.stdout)

        self._run_automatic_fix(extra_args=["--fix-unused", f"--dwyu-log-file={log_file}"])

        if len(deps := self._get_target_deps("//:binary")) > 0:
            return self._make_unexpected_deps_error(expected_deps=set(), actual_deps=deps)
        if len(deps := self._get_target_deps("//:another_binary")) > 0:
            return self._make_unexpected_deps_error(expected_deps=set(), actual_deps=deps)
        if len(deps := self._get_target_deps("//sub/foo:foo")) > 0:
            return self._make_unexpected_deps_error(expected_deps=set(), actual_deps=deps)
        return Success()
