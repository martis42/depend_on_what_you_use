from result import Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:use_configured_lib"

    def execute_test_logic(self) -> Result:
        """
        Without using 'bazel cquery' the test would be red as 'bazel query' would report the superset of all possible
        dependencies which would result in an ambiguous situation with multiple libraries providing the desired header.
        """

        self._create_reports()
        self._run_automatic_fix(
            extra_args=[
                "--fix-missing-deps",
                "--use-cquery",
                "--bazel-args='--//configured_lib:custom_config=true'",
            ]
        )

        target_deps = self._get_target_attribute(target=self.test_target, attribute="deps")
        if (expected := {"//configured_lib:configured_deps", "//ambiguous_lib:lib_a"}) != target_deps:
            return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
        return Success()
