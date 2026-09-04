from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        target = "//target_mapping:use_lib_b_and_ext_b"
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target=target,
                invalid_includes={"target_mapping/use_lib_b_and_ext_b.cpp": ["target_mapping/libs/b.h", "ext_b.h"]},
                # We see an unused dependency error because we use none of the headers mapped into //target_mapping/libs:mapped_dep
                unused_public_deps=["//target_mapping/libs:mapped_dep"],
            )
        )
        actual = self._run_dwyu(
            target=target, aspect=self.choose_aspect("//target_mapping:aspect.bzl%map_specific_deps")
        )

        return self._check_result(actual=actual, expected=expected)
