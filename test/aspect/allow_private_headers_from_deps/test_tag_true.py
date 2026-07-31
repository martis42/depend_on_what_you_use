from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        # We are not seeing unused dependency errors because DWYU thinks the dependencies offer not headers at all and thus prunes them early in the analysis
        expected = ExpectedFailure(
            ExpectedDwyuFailure(
                target="//allow_private_headers_from_deps:forbid_private_headers_from_deps_via_tag",
                invalid_includes={
                    "allow_private_headers_from_deps/use_private_headers_from_deps.h": [
                        "allow_private_headers_from_deps/private_a.h"
                    ],
                    "allow_private_headers_from_deps/use_private_headers_from_deps.cpp": [
                        "allow_private_headers_from_deps/private_b.h"
                    ],
                },
            )
        )
        actual = self._run_dwyu(
            target="//allow_private_headers_from_deps:forbid_private_headers_from_deps_via_tag",
            # Use an aspect allowing private headers from deps to show we can overrule the global setting via a tag on the target under inspection
            aspect="//allow_private_headers_from_deps:aspect.bzl%dwyu_with_priv_hdrs",
        )

        return self._check_result(actual=actual, expected=expected)
