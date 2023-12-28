from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, unused_public_deps=["//test/aspect/recursion:e"])
        actual = self._run_dwyu(
            target="//test/aspect/recursion:use_impl_deps",
            aspect="//test/aspect/recursion:aspect.bzl%dwyu_recursive_impl_deps",
            extra_args=["--experimental_cc_implementation_deps"],
        )

        return self._check_result(actual=actual, expected=expected)
