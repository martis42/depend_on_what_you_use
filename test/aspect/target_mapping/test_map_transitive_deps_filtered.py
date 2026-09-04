from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//target_mapping:use_lib_b_and_ext_b"
        # We see an error, because we mapped only one of the two used transitive dependencies
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target=target,
                invalid_includes={"target_mapping/use_lib_b_and_ext_b.cpp": ["target_mapping/libs/b.h"]},
            )
        )
        actual = self._run_dwyu(
            target=target, aspect=self.choose_aspect("//target_mapping:aspect.bzl%map_transitive_deps_filtered")
        )

        return self._check_result(actual=actual, expected=expected)
