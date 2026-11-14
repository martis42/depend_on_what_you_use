from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//ignore_external_dependencies:use_external_dep_privately"
        actual = self._run_dwyu(
            target=target,
            aspect=self.choose_aspect("//ignore_external_dependencies:aspect.bzl%ignore_external_optimizing_impl_deps"),
        )
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target=target, deps_which_should_be_private=["@ignore_external_dependencies_test_repo//:foo"]
            )
        )

        return self._check_result(actual=actual, expected=expected)
