from result import Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//..."

    def execute_test_logic(self) -> Result:
        dwyu_cmd = self._make_create_reports_cmd(extra_args=["--keep_going"])
        dwyu_process = self._run_and_capture_cmd(dwyu_cmd, check=False)

        log_file = self._workspace / "dwyu_log.log"
        with log_file.open(mode="wt") as log:
            log.write(dwyu_process.stdout)

        self._run_automatic_fix(extra_args=["--fix-unused", f"--dwyu-log-file={log_file}"])

        if len(deps := self._get_target_attribute(target="//:binary", attribute="deps")) > 0:
            return self._make_unexpected_deps_error(expected_deps=[], actual_deps=deps)
        if len(deps := self._get_target_attribute(target="//:another_binary", attribute="deps")) > 0:
            return self._make_unexpected_deps_error(expected_deps=[], actual_deps=deps)
        if len(deps := self._get_target_attribute(target="//sub/foo:foo", attribute="deps")) > 0:
            return self._make_unexpected_deps_error(expected_deps=[], actual_deps=deps)
        return Success()
