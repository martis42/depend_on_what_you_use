from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//tool_cli/workspace:binary"

    def execute_test_logic(self) -> Result:
        self._create_reports(aspect="//tool_cli/workspace:aspect.bzl%default_aspect")

        self._run_automatic_fix(
            bazel_args=["--@rules_python//python/config_settings:experimental_python_import_all_repositories=false"],
            extra_args=["--fix-unused"],
        )

        target_deps = self._get_target_deps(self.test_target)
        if (expected := set()) != target_deps:
            return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
        return Success()
