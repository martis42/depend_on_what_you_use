from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//test/aspect/ignore_includes:use_multiple_arcane_headers",
            aspect="//test/aspect/ignore_includes:aspect.bzl%ignore_include_paths_aspect",
        )

        return self._check_result(actual=actual, expected=expected)