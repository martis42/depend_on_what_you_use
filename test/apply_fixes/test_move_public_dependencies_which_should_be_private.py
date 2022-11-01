from src.result import Error, Result, Success
from src.test_case import TestCaseBase


class TestCase(TestCaseBase):
    @property
    def test_target(self) -> str:
        return "//:public_dependency_with_private_use"

    def execute_test_logic(self) -> Result:
        self._create_reports(
            aspect="use_implementation_deps_aspect", extra_args=["--experimental_cc_implementation_deps"]
        )
        self._run_automatic_fix()
        target_public_deps = self._get_target_attribute(target=self.test_target, attribute="deps")
        target_private_deps = self._get_target_attribute(target=self.test_target, attribute="implementation_deps")

        if target_public_deps == {"//:lib_c"}:
            if target_private_deps == {"//:lib_a", "//:lib_b"}:
                return Success()
            else:
                return Error(
                    f"Dependencies have not been adapted correctly. Unexpected private dependencies: {target_private_deps}"
                )
        else:
            return Error(
                f"Dependencies have not been adapted correctly. Unexpected public dependencies: {target_public_deps}"
            )
