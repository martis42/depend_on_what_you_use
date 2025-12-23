from pathlib import Path

from expected_result import ExpectedResult
from test_case import TestCaseBase

from test.support.result import Result


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        # We omit "In file '..." to allow testing in various environments, since this is generated code in the
        #  bazel-out/.../bin/ dir, whose exact path is platform dependent
        expected_invalid_includes = [
            f'{Path("tree_artifact/sources.cc/tree_lib.cc")}\' include: "tree_artifact/some_lib.h"'
            if self._cpp_impl_based
            else f"{Path('tree_artifact/sources.cc/tree_lib.cc')}', include='tree_artifact/some_lib.h'"
        ]
        expected = ExpectedResult(
            success=False,
            invalid_includes=expected_invalid_includes,
        )
        actual = self._run_dwyu(
            target="//tree_artifact:tree_artifact_library",
            aspect=self.default_aspect,
        )

        return self._check_result(actual=actual, expected=expected)
