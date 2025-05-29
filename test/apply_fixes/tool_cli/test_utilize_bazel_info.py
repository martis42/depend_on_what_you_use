from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:binary"

    def execute_test_logic(self) -> Result:
        self._create_reports(extra_args=["--noexperimental_convenience_symlinks"])
        self._run_automatic_fix(extra_args=["--fix-unused", "--use-bazel-info"])

        target_deps = self._get_target_deps(self.test_target)
        if (expected := set()) != target_deps:  # type: ignore[var-annotated]
            return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
        return Success()
