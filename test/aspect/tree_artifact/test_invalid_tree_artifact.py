from pathlib import Path

from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(
            success=False,
            # We omit "File='bazel-out/<compilation_mode_and_platform> to allow testing in various environments
            invalid_includes=[
                f"{Path('/bin/tree_artifact/sources.cc/tree_lib.cc')}', include='tree_artifact/some_lib.h'"
            ],
        )
        actual = self._run_dwyu(
            target="//tree_artifact:tree_artifact_library",
            aspect=self.default_aspect,
        )

        return self._check_result(actual=actual, expected=expected)
