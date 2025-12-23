from pathlib import Path

from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected_invalid_includes = [
            f"In file '{Path('using_transitive_dep/main.cpp')}' include: \"using_transitive_dep/foo.h\""
            if self._cpp_impl_based
            else f"File='{Path('using_transitive_dep/main.cpp')}', include='using_transitive_dep/foo.h'"
        ]
        expected = ExpectedResult(
            success=False,
            invalid_includes=expected_invalid_includes,
        )
        actual = self._run_dwyu(target="//using_transitive_dep:main", aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
