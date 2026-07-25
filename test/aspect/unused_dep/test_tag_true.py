from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//unused_dep:unused_deps_disallowed_by_tag"
        expected = ExpectedFailure(ExpectedDwyuFailure(target=target, unused_public_deps=["//unused_dep:foo"]))
        actual = self._run_dwyu(
            target=target,
            aspect=self.default_aspect,
            # Disable the unused deps check globally and then activate it for the target under test via a tag
            extra_args=["--aspects_parameters=dwyu_analysis_reports_unused_deps=False"],
        )

        return self._check_result(actual=actual, expected=expected)
