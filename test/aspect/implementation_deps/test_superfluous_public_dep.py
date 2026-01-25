from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//implementation_deps:superfluous_public_dep"
        expected = ExpectedFailure(
            ExpectedDwyuFailure(target=target, deps_which_should_be_private=["//implementation_deps/support:lib_b"])
        )
        actual = self._run_dwyu(
            target=target, aspect=self.choose_aspect("//implementation_deps:aspect.bzl%optimize_impl_deps")
        )

        return self._check_result(actual=actual, expected=expected)
