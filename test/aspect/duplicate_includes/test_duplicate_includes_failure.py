from pathlib import Path

from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        We are not interested in those really appearing 2 times. We simply want to make sure that the same include statement
        appearing multiple times is not causing some undesired behavior during the analysis.
        """
        expected_invalid_includes = (
            [
                "In file 'duplicate_includes/use_foo.h' include: \"duplicate_includes/foo.h\"",
                "In file 'duplicate_includes/use_foo.h' include: \"duplicate_includes/foo.h\"",
            ]
            if self._cpp_impl_based
            else [f"File='{Path('duplicate_includes/use_foo.h')}', include='duplicate_includes/foo.h'"]
        )

        expected = ExpectedResult(success=False, invalid_includes=expected_invalid_includes)
        actual = self._run_dwyu(target="//duplicate_includes:use_foo_transitively", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
