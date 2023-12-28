from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, unused_private_deps=["//test/aspect/unused_dep:foo"])
        actual = self._run_dwyu(
            target="//test/aspect/unused_dep/implementation_deps:implementation_deps_lib",
            aspect="//test/aspect/unused_dep:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        )

        return self._check_result(actual=actual, expected=expected)
