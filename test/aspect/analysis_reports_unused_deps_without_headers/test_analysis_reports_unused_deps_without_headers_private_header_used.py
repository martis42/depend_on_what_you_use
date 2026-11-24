from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//analysis_reports_unused_deps_without_headers:main_private"
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target=target,
                invalid_includes={
                    "analysis_reports_unused_deps_without_headers/main_private.cpp": [
                        "analysis_reports_unused_deps_without_headers/private.h"
                    ],
                },
                unused_public_deps=[
                    "//analysis_reports_unused_deps_without_headers:aggregate",
                    "//analysis_reports_unused_deps_without_headers:private_only",
                ],
            )
        )
        actual = self._run_dwyu(
            target=target,
            aspect=self.choose_aspect(
                "//analysis_reports_unused_deps_without_headers:aspect.bzl%report",
            ),
        )

        return self._check_result(actual=actual, expected=expected)
