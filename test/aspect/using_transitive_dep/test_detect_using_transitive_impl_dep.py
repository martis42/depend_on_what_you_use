from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//using_transitive_dep:transitive_usage_through_impl_deps"
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target=target,
                invalid_includes={
                    "using_transitive_dep/transitive_usage_through_impl_deps.h": [
                        "using_transitive_dep/transitive_dep_hdr.h",
                        "using_transitive_dep/transitive_dep_src.h",
                    ]
                },
            )
        )
        actual = self._run_dwyu(target=target, aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
