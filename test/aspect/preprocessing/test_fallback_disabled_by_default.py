from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        Without the opt-in fallback, boost::wave silently drops the include statements after the problematic construct
        and the dependency providing the dropped header is falsely reported as unused. This makes sure the fallback is
        really opt-in and documents the behavior users get by default.
        """
        target = "//preprocessing/fallback:use_empty_variadic_macro"
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target=target, unused_public_deps=["//preprocessing/fallback:lib_used_after_problematic_construct"]
            )
        )
        actual = self._run_dwyu(target=target, aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
