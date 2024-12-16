from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, deps_which_should_be_private=["//implementation_deps:foo"])
        actual = self._run_dwyu(
            target="//implementation_deps:superfluous_public_dep",
            aspect="//:aspect.bzl%dwyu_impl_deps",
            extra_args=["--experimental_cc_implementation_deps"],
        )

        return self._check_result(actual=actual, expected=expected)
