from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//using_transitive_dep:main_with_tag_opt_in"
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target=target,
                invalid_includes={
                    "using_transitive_dep/main.cpp": [
                        "using_transitive_dep/transitive_dep_hdr.h",
                        "using_transitive_dep/transitive_dep_src.h",
                    ]
                },
            )
        )
        actual = self._run_dwyu(
            target=target,
            aspect=self.default_aspect,
            # Disable the check for using transitive deps globally, so this can only fail as expected due to activating the check via a tag on the target.
            extra_args=["--aspects_parameters=dwyu_analysis_reports_missing_direct_deps=False"],
        )

        return self._check_result(actual=actual, expected=expected)
