from pathlib import Path

from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(
            success=False,
            invalid_includes=[f"File='{Path('target_mapping/use_lib_c.cpp')}', include='target_mapping/libs/c.h'"],
            unused_public_deps=["//target_mapping/libs:a"],
        )
        actual = self._run_dwyu(
            target="//target_mapping:use_lib_c",
            aspect="//target_mapping:aspect.bzl%map_specific_deps",
        )

        return self._check_result(actual=actual, expected=expected)
