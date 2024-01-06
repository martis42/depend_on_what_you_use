from result import Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:mixed_libs_usage"

    def execute_test_logic(self) -> Result:
        self._create_reports()
        self._run_automatic_fix(extra_args=["--fix-missing-deps"])

        target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")
        if (expected := {"//:libs_provider", "//libs:foo", "//libs:bar", "//:root_file_lib"}) != target_deps:
            return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
        return Success()
