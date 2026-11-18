from test_case import TestCaseBase

from test.support.result import Error, Result, Success


class TestCase(TestCaseBase):
    def execute_test_logic(self) -> Result:
        """
        We execute a test case which should fail while listening to output group 'dwyu_report' to prove that this output group does not report failures.
        """
        target = "//output_groups:main"
        actual = self._run_dwyu(target=target, aspect=self.default_aspect, output_group="dwyu_report")
        if actual.returncode != 0:
            return Error(f"Build failed unexpectedly: {actual.stdout}\n{actual.stderr}")

        return Success()
