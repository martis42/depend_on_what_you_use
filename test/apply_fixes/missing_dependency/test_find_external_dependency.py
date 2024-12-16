from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:use_external_dep"

    @property
    def extra_workspace_file_content(self) -> str:
        return """
bazel_dep(name = "external_dep")
local_path_override(module_name = "external_dep", path = "external_dep")
"""

    def execute_test_logic(self) -> Result:
        self._create_reports()
        self._run_automatic_fix(extra_args=["--fix-missing-deps"])

        target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")
        expected_deps = {"@external_dep//:foo", "@external_dep//sub/dir:bar", "//:external_dep_provider"}
        if expected_deps != target_deps:
            return self._make_unexpected_deps_error(expected_deps=expected_deps, actual_deps=target_deps)
        return Success()
