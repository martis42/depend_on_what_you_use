from expected_result import ExpectedSuccess
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    """
    Regression test for the preprocessing silently dropping include statements of the file under inspection.

    The source file includes its own header first, which transitively pulls in a header full of unresolvable include
    statements. The errors raised for those unresolvable includes while recursing through the header tree are
    swallowed by the preprocessing. This must not corrupt discovering the include statements which come after the own
    header in the source file. In the past this happened and the implementation_deps providing those dropped include
    statements were falsely reported as unused.
    """

    def execute_test_logic(self) -> Result:
        actual = self._run_dwyu(
            target="//unresolvable_transitive_includes:use_impl_dep_after_own_header",
            aspect=self.default_aspect,
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
