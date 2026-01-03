from pathlib import Path

from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected_invalid_includes = (
            [
                "In file 'using_transitive_dep/transitive_usage_through_impl_deps.h' include: \"using_transitive_dep/transitive_dep_hdr.h\"",
                "In file 'using_transitive_dep/transitive_usage_through_impl_deps.h' include: \"using_transitive_dep/transitive_dep_src.h\"",
            ]
            if self._cpp_impl_based
            else [
                f"File='{Path('using_transitive_dep/transitive_usage_through_impl_deps.h')}', include='using_transitive_dep/transitive_dep_hdr.h'",
                f"File='{Path('using_transitive_dep/transitive_usage_through_impl_deps.h')}', include='using_transitive_dep/transitive_dep_hdr.h'",
            ]
        )
        expected = ExpectedResult(
            success=False,
            invalid_includes=expected_invalid_includes,
        )
        actual = self._run_dwyu(
            target="//using_transitive_dep:transitive_usage_through_impl_deps", aspect=self.default_aspect_impl_deps
        )

        return self._check_result(actual=actual, expected=expected)
