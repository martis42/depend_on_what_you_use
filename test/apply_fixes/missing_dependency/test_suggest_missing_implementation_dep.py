from result import Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:use_libs_privately"

    def execute_test_logic(self) -> Result:
        self._create_reports(
            aspect="use_implementation_deps_aspect", extra_args=["--experimental_cc_implementation_deps"]
        )
        self._run_automatic_fix(extra_args=["--fix-missing-deps"])

        target_implementation_deps = self._get_target_attribute(
            target=self.test_target, attribute="implementation_deps"
        )
        expected_implementation_deps = {"//:libs_provider", "//libs:foo", "//libs:bar", "//:root_file_lib"}
        if expected_implementation_deps != target_implementation_deps:
            return self._make_unexpected_deps_error(
                expected_implementation_deps=expected_implementation_deps,
                actual_implementation_deps=target_implementation_deps,
            )
        return Success()
