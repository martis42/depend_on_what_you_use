from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//missing_dependency/workspace:use_libs_privately"

    def execute_test_logic(self) -> Result:
        self._create_reports(aspect="//missing_dependency/workspace:aspect.bzl%optimizes_impl_deps_aspect")
        self._run_automatic_fix(extra_args=["--fix-missing-deps"])

        target_implementation_deps = self._get_target_impl_deps(self.test_target)
        expected_implementation_deps = {
            "//missing_dependency/workspace/libs:bar",
            "//missing_dependency/workspace/libs:foo",
            "//missing_dependency/workspace:libs_provider",
            "//missing_dependency/workspace:root_file_lib",
        }
        if expected_implementation_deps != target_implementation_deps:
            return self._make_unexpected_deps_error(
                expected_implementation_deps=expected_implementation_deps,
                actual_implementation_deps=target_implementation_deps,
            )
        return Success()
