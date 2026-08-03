from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    """
    Skipping a target shall not stop the recursive analysis of the targets below it.

    '//skip_targets:middle' is excluded from the analysis and has an unused dependency itself. Thus, the single expected
    report proves both that the analysis of the skipped target is skipped and that its dependencies are still analyzed.
    """

    def execute_test_logic(self) -> Result:
        expected = ExpectedFailure(
            ExpectedDwyuFailure(target="//skip_targets:bottom", unused_public_deps=["//skip_targets:unused_lib"])
        )
        actual = self._run_dwyu(
            target="//skip_targets:top",
            aspect=self.choose_aspect("//skip_targets:aspect.bzl%dwyu_skip_in_recursion"),
        )

        return self._check_result(actual=actual, expected=expected)
