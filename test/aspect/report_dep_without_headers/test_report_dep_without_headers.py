from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//report_dep_without_headers:main"
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target=target,
                unused_public_deps=["//report_dep_without_headers:aggregate"],
            )
        )
        actual = self._run_dwyu(
            target=target,
            aspect=self.choose_aspect(
                "//report_dep_without_headers:aspect.bzl%report",
            ),
        )

        return self._check_result(actual=actual, expected=expected)
