from pathlib import Path

from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected_invalid_includes = [
            "In file 'target_mapping/use_lib_c.cpp' include: \"target_mapping/libs/c.h\""
            if self._cpp_impl_based
            else f"File='{Path('target_mapping/use_lib_c.cpp')}', include='target_mapping/libs/c.h'"
        ]
        expected = ExpectedResult(
            success=False,
            invalid_includes=expected_invalid_includes,
            unused_public_deps=["//target_mapping/libs:a"],
        )
        actual = self._run_dwyu(
            target="//target_mapping:use_lib_c",
            aspect=self.choose_aspect("//target_mapping:aspect.bzl%map_specific_deps"),
        )

        return self._check_result(actual=actual, expected=expected)
