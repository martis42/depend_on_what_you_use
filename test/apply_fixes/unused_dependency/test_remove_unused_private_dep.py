from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//unused_dependency/workspace:unused_private_dep"

    def execute_test_logic(self) -> Result:
        self._create_reports(aspect="//unused_dependency/workspace:aspect.bzl%optimizes_impl_deps_aspect")
        self._run_automatic_fix(extra_args=["--fix-unused-deps"])

        target_deps = self._get_target_impl_deps(self.test_target)
        if (expected := {"//unused_dependency/workspace:lib_a"}) != target_deps:
            return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
        return Success()
