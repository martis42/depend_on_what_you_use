from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target=[
                "//test/aspect/implementation_deps:proper_private_deps",
                "//test/aspect/implementation_deps:binary_using_foo",
                "//test/aspect/implementation_deps:test_using_foo",
            ],
            aspect="//test/aspect/implementation_deps:aspect.bzl%implementation_deps_aspect",
            extra_args=["--experimental_cc_implementation_deps"],
        )

        return self._check_result(actual=actual, expected=expected)
