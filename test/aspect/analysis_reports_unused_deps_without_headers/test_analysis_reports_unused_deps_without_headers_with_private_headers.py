from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//analysis_reports_unused_deps_without_headers:main"
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target=target,
                unused_public_deps=["//analysis_reports_unused_deps_without_headers:aggregate"],
            )
        )
        actual = self._run_dwyu(
            target=target,
            aspect=self.choose_aspect(
                "//analysis_reports_unused_deps_without_headers:aspect.bzl%report_with_private_headers",
            ),
        )

        return self._check_result(actual=actual, expected=expected)
