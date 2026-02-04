from expected_result import ExpectedSuccess
from test_case import Compatibility, Compatible, Incompatible, TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    @property
    def compatibility(self) -> Compatibility:
        if self._cpp_impl_based:
            return Compatible()
        return Incompatible("Not compatible with the Python based implementation")

    def execute_test_logic(self) -> Result:
        target = "//unused_dep:unused_deps"
        actual = self._run_dwyu(
            target=target,
            aspect=self.default_aspect,
            extra_args=["--aspects_parameters=dwyu_analysis_reports_unused_deps=False"],
        )

        return self._check_result(actual=actual, expected=ExpectedSuccess())
