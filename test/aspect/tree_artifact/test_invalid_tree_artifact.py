from result import ExpectedResult, Result
from test_case import TestCaseBase


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        expected = ExpectedResult(
            success=False,
            invalid_includes=[
                "File='bazel-out/k8-fastbuild/bin/test/aspect/tree_artifact/sources.cc/tree_lib.cc', include='test/aspect/tree_artifact/some_lib.h'"
            ],
        )
        actual = self._run_dwyu(
            target="//test/aspect/tree_artifact:tree_artifact_library",
            aspect=self.default_aspect,
            extra_args=["--compilation_mode=fastbuild"],
        )

        return self._check_result(actual=actual, expected=expected)
