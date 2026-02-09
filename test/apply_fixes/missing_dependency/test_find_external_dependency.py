from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//missing_dependency/workspace:use_external_dep"

    def execute_test_logic(self) -> Result:
        self._create_reports(aspect="//missing_dependency/workspace:aspect.bzl%default_aspect")
        self._run_automatic_fix(extra_args=["--fix-missing-deps"])

        target_deps = self._get_target_deps(self.test_target)
        expected_deps = {
            "//missing_dependency/workspace:external_dep_provider",
            "@external_dep//:foo",
            "@external_dep//sub/dir:bar",
        }
        if expected_deps != target_deps:
            return self._make_unexpected_deps_error(expected_deps=expected_deps, actual_deps=target_deps)
        return Success()
