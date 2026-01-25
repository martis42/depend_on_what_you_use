from expected_result import ExpectedDwyuFailure, ExpectedFailure
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        # The exact path of a generated file depends on the target platform. Thus, we have to compute it here.
        bazel_bin = self._run_bazel_info("bazel-bin").stdout.strip()
        generated_sources_prefix = "bazel-out/" + bazel_bin.split("/bazel-out/")[1]
        generated_file = generated_sources_prefix + "/" + "tree_artifact/sources.cc/tree_lib.cc"

        target = "//tree_artifact:tree_artifact_library"
        expected = ExpectedFailure(
            [ExpectedDwyuFailure(target=target, invalid_includes={generated_file: ["tree_artifact/some_lib.h"]})]
        )
        actual = self._run_dwyu(target=target, aspect=self.default_aspect)

        return self._check_result(actual=actual, expected=expected)
