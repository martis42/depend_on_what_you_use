from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//missing_dependency/workspace:use_generated_code"

    def execute_test_logic(self) -> Result:
        self._create_reports(aspect="//missing_dependency/workspace:aspect.bzl%default_aspect")
        self._run_automatic_fix(extra_args=["--fix-missing-deps"])

        target_deps = self._get_target_deps(self.test_target)
        if (
            expected := {
                "//missing_dependency/workspace/generate_code:foo",
                "//missing_dependency/workspace:generated_code_provider",
            }
        ) != target_deps:
            return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
        return Success()
