from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    @property
    def test_aspect(self) -> str:
        aspect = "//ignore_includes:aspect.bzl%extra_ignore_include_paths_aspect"
        return aspect + "_cct" if self._cc_toolchain_based else aspect

    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=True)
        actual = self._run_dwyu(
            target="//ignore_includes:use_arcane_header_and_vector",
            aspect=self.test_aspect,
        )

        return self._check_result(actual=actual, expected=expected)
