from src.result import Error, Result, Success
from src.test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:unused_public_dep"

    def execute_test_logic(self) -> Result:
        self._create_reports(extra_args=["--nobuild"])

        catched_exception = False
        try:
            self._run_automatic_fix()
        except Exception as ex:
            catched_exception = True
            if not "returned non-zero exit status 1" in str(ex):
                return Error(f"Expected an exception, but none occured")
        if not catched_exception:
            return Error(f"Expected an exception, but none occured")

        return Success()
