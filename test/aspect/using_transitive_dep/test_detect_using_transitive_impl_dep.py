from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(
            success=False,
            invalid_includes=[
                "File='test/aspect/using_transitive_dep/transitive_usage_through_impl_deps.h', include='test/aspect/using_transitive_dep/foo.h'"
            ],
        )
        actual = self._run_dwyu(
            target="//test/aspect/using_transitive_dep:transitive_usage_through_impl_deps",
            aspect="//test/aspect:aspect.bzl%dwyu_impl_deps",
            extra_args=["--experimental_cc_implementation_deps"],
        )

        return self._check_result(actual=actual, expected=expected)