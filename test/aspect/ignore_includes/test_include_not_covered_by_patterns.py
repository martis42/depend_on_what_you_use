from pathlib import Path

from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(
            success=False,
            invalid_includes=[
                f"File='{Path('ignore_includes/use_not_ignored_header.h')}', include='support/a_substring_match_does_not_work_here.h'"
            ],
        )
        actual = self._run_dwyu(
            target="//ignore_includes:use_not_ignored_header",
            aspect=self.choose_aspect("//ignore_includes:aspect.bzl%extra_ignore_include_patterns_aspect"),
        )

        return self._check_result(actual=actual, expected=expected)
