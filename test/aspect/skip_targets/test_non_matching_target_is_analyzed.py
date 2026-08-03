from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedFailure(
            ExpectedDwyuFailure(target="//skip_targets:broken_sibling", unused_public_deps=["//skip_targets:unused_lib"])
        )
        actual = self._run_dwyu(
            target="//skip_targets:broken_sibling",
            aspect=self.choose_aspect("//skip_targets:aspect.bzl%dwyu_skip_exact"),
        )

        return self._check_result(actual=actual, expected=expected)
