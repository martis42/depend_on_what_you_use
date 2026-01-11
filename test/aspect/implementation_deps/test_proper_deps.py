from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target=[
                "//implementation_deps:proper_private_deps",
                "//implementation_deps:binary_using_foo",
                "//implementation_deps:test_using_foo",
                "//implementation_deps:use_complex_includes",
                "//implementation_deps:use_defines",
                "//implementation_deps:use_external",
            ],
            aspect=self.choose_aspect("//implementation_deps:aspect.bzl%optimize_impl_deps"),
        )

        return self._check_result(actual=actual, expected=expected)
