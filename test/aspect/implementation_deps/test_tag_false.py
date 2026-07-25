from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target=["//implementation_deps:superfluous_public_dep_with_tag_opt_out"],
            aspect=self.choose_aspect("//implementation_deps:aspect.bzl%optimize_impl_deps"),
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
