from pathlib import Path

from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    @property
    def test_aspect(self) -> str:
        aspect = "//target_mapping:aspect.bzl%map_direct_deps"
        return aspect + "_cct" if self._cc_toolchain_based else aspect

    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(
            success=False,
            invalid_includes=[f"File='{Path('target_mapping/use_lib_c.cpp')}', include='target_mapping/libs/c.h'"],
            unused_public_deps=["//target_mapping/libs:a"],
        )
        actual = self._run_dwyu(
            target="//target_mapping:use_lib_c",
            aspect=self.test_aspect,
        )

        return self._check_result(actual=actual, expected=expected)
