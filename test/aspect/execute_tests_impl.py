import subprocess
from argparse import ArgumentParser, Namespace
from copy import deepcopy
from dataclasses import dataclass, field
from os import environ
from pathlib import Path
from shlex import join as join_cmd
from shutil import which
from typing import Dict, List, Optional

# Each line in the output corresponding to an error is expected to start with this
ERRORS_PREFIX = " " * 2

# DWYU terminal output key fragments
DWYU_FAILURE = "Result: FAILURE"
CATEGORY_INVALID_INCLUDES = "Includes which are not available from the direct dependencies"
CATEGORY_NON_PRIVATE_DEPS = "Public dependencies which are used only in private code"
CATEGORY_UNUSED_PUBLIC_DEPS = "Unused dependencies in 'deps' (none of their headers are referenced)"
CATEGORY_UNUSED_PRIVATE_DEPS = "Unused dependencies in 'implementation_deps' (none of their headers are referenced)"


@dataclass
class TestedVersions:
    bazel: str
    python: str


@dataclass
class TestCmd:
    target: str
    aspect: str = ""
    extra_args: List[str] = field(default_factory=list)


@dataclass
class ExpectedResult:
    """
    Encapsulates an expected result of a DWYU analysis and offers functions
    to compare a given output to the expectations.
    """

    success: bool
    invalid_includes: List[str] = field(default_factory=list)
    unused_public_deps: List[str] = field(default_factory=list)
    unused_private_deps: List[str] = field(default_factory=list)
    deps_which_should_be_private: List[str] = field(default_factory=list)

    def matches_expectation(self, return_code: int, dwyu_output: str) -> bool:
        if not self._has_correct_status(return_code=return_code, output=dwyu_output):
            return False

        output_lines = dwyu_output.split("\n")
        if not ExpectedResult._has_expected_errors(
            expected_errors=self.invalid_includes,
            error_category=CATEGORY_INVALID_INCLUDES,
            output=output_lines,
        ):
            return False
        if not ExpectedResult._has_expected_errors(
            expected_errors=self.unused_public_deps,
            error_category=CATEGORY_UNUSED_PUBLIC_DEPS,
            output=output_lines,
        ):
            return False
        if not ExpectedResult._has_expected_errors(
            expected_errors=self.unused_private_deps,
            error_category=CATEGORY_UNUSED_PRIVATE_DEPS,
            output=output_lines,
        ):
            return False
        if not ExpectedResult._has_expected_errors(
            expected_errors=self.deps_which_should_be_private,
            error_category=CATEGORY_NON_PRIVATE_DEPS,
            output=output_lines,
        ):
            return False

        return True

    def _has_correct_status(self, return_code: int, output: str) -> bool:
        if self.success and return_code == 0:
            return True
        if not self.success and return_code != 0 and DWYU_FAILURE in output:
            return True
        return False

    @staticmethod
    def _get_error_lines(idx_category: int, output: List[str]) -> List[str]:
        errors_begin = idx_category + 1
        errors_end = 0
        for i in range(errors_begin, len(output)):
            if output[i].startswith(ERRORS_PREFIX):
                errors_end = i + 1
            else:
                break
        return output[errors_begin:errors_end]

    @staticmethod
    def _has_expected_errors(expected_errors: List[str], error_category: str, output: List[str]) -> bool:
        if not expected_errors:
            return True

        idx_category = ExpectedResult._find_line_with(lines=output, val=error_category)
        if idx_category is None:
            return False

        if not ExpectedResult._has_errors(
            error_lines=ExpectedResult._get_error_lines(idx_category=idx_category, output=output),
            expected_errors=expected_errors,
        ):
            return False
        return True

    @staticmethod
    def _find_line_with(lines: List[str], val: str) -> Optional[int]:
        for idx, line in enumerate(lines):
            if val in line:
                return idx
        return None

    @staticmethod
    def _has_errors(error_lines: List[str], expected_errors: List[str]) -> bool:
        if len(error_lines) != len(expected_errors):
            return False
        return all(any(error in line for line in error_lines) for error in expected_errors)


@dataclass
class CompatibleVersions:
    minimum: str = ""
    maximum: str = ""

    def is_compatible_to(self, version: str) -> bool:
        comply_with_min_version = version >= self.minimum if self.minimum else True
        comply_with_max_version = version <= self.maximum if self.maximum else True
        return comply_with_min_version and comply_with_max_version


@dataclass
class TestCase:
    name: str
    cmd: TestCmd
    expected: ExpectedResult
    compatible_versions: CompatibleVersions = field(default_factory=CompatibleVersions)


@dataclass
class FailedTest:
    name: str
    version: TestedVersions


def verify_test(test: TestCase, process: subprocess.CompletedProcess, verbose: bool) -> bool:
    if test.expected.matches_expectation(return_code=process.returncode, dwyu_output=process.stdout):
        if verbose:
            print("\n" + process.stdout + "\n")
        ok_verb = "succeeded" if test.expected.success else "failed"
        print(f"<<< OK '{test.name}' {ok_verb} as expected")
        return True

    print("\n" + process.stdout + "\n")
    print(f"<<< ERROR '{test.name}' did not behave as expected")
    return False


def bazel_binary() -> str:
    bazel = which("bazelisk") or which("bazel")
    if not bazel:
        raise Exception("No bazel or bazelisk binary available on your system")
    return bazel


def make_cmd(test_cmd: TestCmd, startup_args: List[str], extra_args: List[str]) -> List[str]:
    cmd = [bazel_binary(), *startup_args, "build", "--noshow_progress"]
    if test_cmd.aspect:
        cmd.extend([f"--aspects={test_cmd.aspect}", "--output_groups=dwyu"])
    cmd.extend(extra_args)
    cmd.extend(test_cmd.extra_args)
    cmd.append("--")
    cmd.append(test_cmd.target)
    return cmd


def current_workspace() -> Path:
    process = subprocess.run([bazel_binary(), "info", "workspace"], capture_output=True, text=True, check=True)
    return Path(process.stdout.strip())


def execute_tests(
    versions: List[TestedVersions],
    tests: List[TestCase],
    version_specific_args: Dict[str, CompatibleVersions],
    verbose: bool = False,
) -> List[FailedTest]:
    failed_tests = []
    test_env = deepcopy(environ)
    workspace_path = current_workspace()
    output_root = Path(environ["HOME"]) / ".cache" / "bazel" / workspace_path.relative_to("/")
    for version in versions:
        test_env["USE_BAZEL_VERSION"] = version.bazel
        output_base = output_root / f"aspect_integration_tests_bazel_{version.bazel}_python_{version.python}"
        output_base.mkdir(parents=True, exist_ok=True)
        extra_args = [
            arg
            for arg, valid_versions in version_specific_args.items()
            if valid_versions.is_compatible_to(version.bazel)
        ]
        extra_args.append(f"--@rules_python//python/config_settings:python_version={version.python}")

        for test in tests:
            if not test.compatible_versions.is_compatible_to(version.bazel):
                print(f"\n--- Skip '{test.name}' due to incompatible Bazel '{version.bazel}'")
                continue
            print(f"\n>>> Execute '{test.name}' with Bazel {version.bazel} and Python {version.python}")

            dwyu_cmd = make_cmd(test_cmd=test.cmd, startup_args=[f"--output_base={output_base}"], extra_args=extra_args)
            if verbose:
                print(f"Executing cmd: {join_cmd(dwyu_cmd)}")
            process = subprocess.run(
                dwyu_cmd,
                env=test_env,
                encoding="utf-8",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )

            if not verify_test(test=test, process=process, verbose=verbose):
                # TODO clearer naming version -> bazel_version or take TestedVersions
                failed_tests.append(FailedTest(name=test.name, version=version))

    return failed_tests


def cli() -> Optional[Namespace]:
    parser = ArgumentParser()
    parser.add_argument("--verbose", "-v", action="store_true", help="Show output of test runs.")
    parser.add_argument(
        "--bazel",
        "-b",
        metavar="VERSION",
        help="Run tests with the specified Bazel version. Also requires setting '--python'",
    )
    parser.add_argument(
        "--python",
        "-p",
        metavar="VERSION",
        help="Run tests with the specified Python version."
        " Has to be one of the versions for which we register a hermetic toolchain. Also requires setting '--bazel'.",
    )
    parser.add_argument("--test", "-t", nargs="+", help="Run the specified test cases.")

    args = parser.parse_args()
    if (args.bazel and not args.python) or (not args.bazel and args.python):
        print("ERROR: '--bazel' and '--python' have to be used together")
        return None

    return args


def main(
    args: Namespace,
    test_cases: List[TestCase],
    tested_versions: List[TestedVersions],
    version_specific_args: Dict[str, CompatibleVersions],
) -> int:
    versions = [TestedVersions(bazel=args.bazel, python=args.python)] if args.bazel and args.python else tested_versions
    active_tests = [tc for tc in test_cases if tc.name in args.test] if args.test else test_cases

    failed_tests = execute_tests(
        versions=versions, tests=active_tests, version_specific_args=version_specific_args, verbose=args.verbose
    )

    print("\n" + 30 * "#" + "  SUMMARY  " + 30 * "#" + "\n")
    if failed_tests:
        print("FAILURE\n")
        print("These tests failed:")
        print(
            "\n".join(f"- '{t.name}' for Bazel {t.version.bazel} and Python {t.version.python}" for t in failed_tests)
        )
        return 1

    print("SUCCESS\n")
    return 0
