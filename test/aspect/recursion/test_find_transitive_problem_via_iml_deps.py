from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    @property
    def test_aspect(self) -> str:
        aspect = "//recursion:aspect.bzl%dwyu_recursive_impl_deps"
        return aspect + "_cct" if self._cc_toolchain_based else aspect

    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(success=False, unused_public_deps=["//recursion:e"])
        actual = self._run_dwyu(
            target="//recursion:use_impl_deps",
            aspect=self.test_aspect,
            extra_args=["--experimental_cc_implementation_deps"],
        )

        return self._check_result(actual=actual, expected=expected)
