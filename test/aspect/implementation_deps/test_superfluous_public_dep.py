from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, deps_which_should_be_private=["//implementation_deps/support:lib_b"])
        actual = self._run_dwyu(
            target="//implementation_deps:superfluous_public_dep",
            aspect=self.choose_aspect("//implementation_deps:aspect.bzl%optimize_impl_deps"),
        )

        return self._check_result(actual=actual, expected=expected)
