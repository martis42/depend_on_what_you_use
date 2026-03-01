import logging
import shlex
import subprocess
from dataclasses import dataclass
from importlib.machinery import SourceFileLoader
from pathlib import Path
from tempfile import NamedTemporaryFile

from test.apply_fixes.test_case import TestCaseBase
from test.support.bazel import get_bazel_binary, get_current_workspace
from test.support.result import Error

log = logging.getLogger()


@dataclass
class TestDefinition:
    name: str
    script: Path
    test_dir: Path


class ApplyFixesIntegrationTestsExecutor:
    def __init__(self, requested_tests: list[str] | None) -> None:
        self.requested_tests = requested_tests or []

        self.bazel_bin = get_bazel_binary()
        self.origin_workspace = get_current_workspace(self.bazel_bin)
        self.test_definitions = self._get_test_definitions()

    def list_tests(self) -> None:
        log.info("Available test cases:")
        log.info("\n".join(f"- {t.name}" for t in self.test_definitions))

    def ensure_no_local_changes(self) -> list[str]:
        unique_test_dirs = {test.test_dir for test in self.test_definitions}
        errors = []
        for test_dir in unique_test_dirs:
            cmd = ["git", "status", "--porcelain", "."]
            log.debug(f"Checking for local changes with command: '{shlex.join(cmd)}'")
            result = subprocess.run(cmd, cwd=test_dir, check=True, shell=False, capture_output=True, text=True)
            if result.stdout.strip():
                details = "\n".join(f"  {line}" for line in result.stdout.splitlines())
                error = f"Local changes in '{test_dir}':\n{details}"
                errors.append(error)

        return errors

    def execute_tests(self) -> list[str]:
        """
        :return: List of failed test cases
        """
        tests = []
        for test in self.test_definitions:
            if not self.requested_tests or any(requested in test.name for requested in self.requested_tests):
                module = SourceFileLoader("", str(test.script.resolve())).load_module()
                tests.append(
                    module.TestCase(
                        name=test.name,
                        test_dir=test.test_dir,
                        bazel_binary=self.bazel_bin,
                    )
                )

        return [test.name for test in tests if not self._execute_test(test)]

    def _execute_test(self, test: TestCaseBase) -> bool:
        if (incompatibility := test.is_incompatible) != "":
            log.info(f"--- Skipping '{test.name}' due to: {incompatibility}")
            return True
        log.info(f">>> Test '{test.name}'")

        result = None
        log_file = self._setup_log_file()
        try:
            try:
                result = test.execute_test(log_file)
            except Exception:
                result = Error("Exception occurred")
                log.exception("Test failed due to exception:")
        finally:
            log_file.unlink(missing_ok=True)

        self._cleanup(test.test_dir)

        if not result.is_success():
            log.info(result.error)
        log.info(f"<<< {'OK' if result.is_success() else 'FAILURE'}\n")

        return result.is_success()

    @staticmethod
    def _setup_log_file() -> Path:
        """
        On windows we have to close the log file and manually clean it up to prevent file locking issues on GitHub Windows workers.
        """
        log_file = NamedTemporaryFile(delete=False)  # noqa: SIM115
        log_file_path = Path(log_file.name)
        log_file.close()
        return log_file_path

    def _cleanup(self, test_dir: Path) -> None:
        cmd = ["git", "checkout", "."]
        log.debug(f"Running cleanup command: '{shlex.join(cmd)}' in {test_dir}")
        subprocess.run(cmd, cwd=test_dir, check=True, shell=False, capture_output=True)

    def _get_test_definitions(self) -> list[TestDefinition]:
        test_scripts = [Path(file) for file in sorted(Path().cwd().glob("*/test_*.py"))]
        return [
            TestDefinition(
                name=file.parent.name + "/" + file.stem.replace("test_", "", 1),
                script=file,
                test_dir=file.parent / "workspace",
            )
            for file in test_scripts
        ]


def main(requested_tests: list[str] | None = None, list_tests: bool = False) -> int:
    executor = ApplyFixesIntegrationTestsExecutor(requested_tests)

    if list_tests:
        executor.list_tests()
        return 0

    if (errors := executor.ensure_no_local_changes()) != []:
        log.error("Commit or stash local changes them to prevent losing them.\n")
        log.error("\n".join(errors))
        return 1

    failed_tests = executor.execute_tests()
    log.info(f"Running tests {'FAILED' if failed_tests else 'SUCCEEDED'}")
    if failed_tests:
        log.info("\nFailed tests:")
        log.info("\n".join(f"- '{test}'" for test in failed_tests))
        return 1

    return 0
