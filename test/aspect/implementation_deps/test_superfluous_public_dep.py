from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, deps_which_should_be_private=["//test/aspect/implementation_deps:foo"])
        actual = self._run_dwyu(
            target="//test/aspect/implementation_deps:superfluous_public_dep",
            aspect="//test/aspect/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        )

        return self._check_result(actual=actual, expected=expected)
