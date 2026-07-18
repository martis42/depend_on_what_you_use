from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target="//allow_private_headers_from_deps:use_private_headers_from_deps",
                invalid_includes={
                    "allow_private_headers_from_deps/use_private_headers_from_deps.h": [
                        "allow_private_headers_from_deps/private_a.h"
                    ],
                    "allow_private_headers_from_deps/use_private_headers_from_deps.cpp": [
                        "allow_private_headers_from_deps/private_b.h"
                    ],
                },
                unused_public_deps=["//allow_private_headers_from_deps:dep_a"],
                unused_private_deps=["//allow_private_headers_from_deps:dep_b"],
            )
        )
        actual = self._run_dwyu(
            target="//allow_private_headers_from_deps:use_private_headers_from_deps", aspect=self.default_aspect
        )

        return self._check_result(actual=actual, expected=expected)
