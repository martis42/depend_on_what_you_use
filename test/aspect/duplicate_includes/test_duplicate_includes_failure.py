from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        We are not interested in those really appearing 2 times. We simply want to make sure that the same include statement
        appearing multiple times is not causing some undesired behavior during the analysis.
        """

        target = "//duplicate_includes:use_foo_transitively"
        expected_invalid_includes = (
            {"duplicate_includes/use_foo.h": ["duplicate_includes/foo.h", "duplicate_includes/foo.h"]}
            if self._cpp_impl_based
            else {"duplicate_includes/use_foo.h": ["duplicate_includes/foo.h"]}
        )
        expected = ExpectedFailure(ExpectedDwyuFailure(target=target, invalid_includes=expected_invalid_includes))
        actual = self._run_dwyu(target=target, aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
