from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(
            success=False,
            invalid_includes=[
                "File='ignore_includes/use_not_ignored_header.h', include='example_substring_matching_does_not_work_here.h'"
            ],
        )
        actual = self._run_dwyu(
            target="//ignore_includes:use_not_ignored_header",
            aspect="//ignore_includes:aspect.bzl%extra_ignore_include_patterns_aspect",
        )

        return self._check_result(actual=actual, expected=expected)
