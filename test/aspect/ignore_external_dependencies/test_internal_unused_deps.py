from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//ignore_external_dependencies:unused_internal_deps"
        actual = self._run_dwyu(
            target=target,
            aspect=self.choose_aspect("//ignore_external_dependencies:aspect.bzl%ignore_external"),
        )
        expected = ExpectedFailure(
            ExpectedDwyuFailure(target=target, unused_public_deps=["//ignore_external_dependencies:local_header"])
        )
        return self._check_result(actual=actual, expected=expected)
