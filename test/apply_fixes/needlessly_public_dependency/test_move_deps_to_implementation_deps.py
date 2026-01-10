from test.apply_fixes.test_case import TestCaseBase
from test.support.result import Result, Success


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:public_dependency_with_private_use"

    def execute_test_logic(self) -> Result:
        self._create_reports(aspect="optimizes_impl_deps_aspect")
        self._run_automatic_fix(extra_args=["--fix-deps-which-should-be-private"])

        target_deps = self._get_target_deps(self.test_target)
        target_implementation_deps = self._get_target_impl_deps(self.test_target)
        expected_deps = {"//:lib_c"}
        expected_implementation_deps = {"//:lib_a", "//:lib_b"}
        if expected_deps != target_deps or expected_implementation_deps != target_implementation_deps:
            return self._make_unexpected_deps_error(
                expected_deps=expected_deps,
                expected_implementation_deps=expected_implementation_deps,
                actual_deps=target_deps,
                actual_implementation_deps=target_implementation_deps,
            )
        return Success()
