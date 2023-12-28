from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//test/aspect/skip_tags:ignored_by_custom_tag",
            aspect="//test/aspect/skip_tags:aspect.bzl%dwyu_custom_tags",
        )

        return self._check_result(actual=actual, expected=expected)
