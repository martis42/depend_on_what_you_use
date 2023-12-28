from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(
            success=False,
            invalid_includes=[
                "File='test/aspect/using_transitive_dep/main.cpp', include='test/aspect/using_transitive_dep/foo.h'"
            ],
        )
        actual = self._run_dwyu(target="//test/aspect/using_transitive_dep:main", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
