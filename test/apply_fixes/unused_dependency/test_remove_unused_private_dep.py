from result import Result, Success
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:unused_private_dep"

    def execute_test_logic(self) -> Result:
        self._create_reports(
            aspect="use_implementation_deps_aspect", extra_args=["--experimental_cc_implementation_deps"]
        )
        self._run_automatic_fix(extra_args=["--fix-unused-deps"])

        target_deps = self._get_target_attribute(target=self.test_target, attribute="implementation_deps")
        if (expected := {"//:lib_a"}) != target_deps:
            return self._make_unexpected_deps_error(expected_deps=expected, actual_deps=target_deps)
        return Success()
