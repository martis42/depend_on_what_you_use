import subprocess as sb
import tempfile
from distutils.dir_util import copy_tree
from pathlib import Path
from typing import List, Optional, Set

WORKSPACE_TEMPLATE = """
local_repository(
    name = "depend_on_what_you_use",
    path = "{dwyu_repo}",
)

load("@depend_on_what_you_use//:dependencies.bzl", dwyu_public_dependencies = "public_dependencies")

dwyu_public_dependencies()
"""


class TestCase:
    def __init__(
        self,
        name: str,
        path: str,
        target: str,
        expected_deps: List[str],
        apply_fixes_extra_args: Optional[List[str]] = None,
        dwyu_extra_startup_args: Optional[List[str]] = None,
        dwyu_extra_args: Optional[List[str]] = None,
        expected_exception: str = "",
    ) -> None:
        self.name = name
        self.path = path
        self.target = target
        # List of dependencies which the target shall have after performing the fix
        self.expected_deps = expected_deps
        self.apply_fixes_extra_args = apply_fixes_extra_args if apply_fixes_extra_args else []
        self.dwyu_extra_startup_args = dwyu_extra_startup_args if dwyu_extra_startup_args else []
        self.dwyu_extra_args = dwyu_extra_args if dwyu_extra_args else []
        # The test is supposed to fail and this substring shall be part of the exception description
        self.expected_exception = expected_exception


class Result:
    def __init__(self, test: str, error: str = "") -> None:
        self.test = test
        self.error = error

    def is_success(self) -> bool:
        return len(self.error) == 0


def get_current_workspace() -> Path:
    process = sb.run(["bazel", "info", "workspace"], check=True, encoding="utf-8", stdout=sb.PIPE, stderr=sb.PIPE)
    return Path(process.stdout.strip())


def setup_test_workspace(
    test: TestCase, workspace: Path, startup_args: List[str], extra_args: List[str], verbose: bool
) -> None:
    current_workspace = get_current_workspace()
    test_sources = current_workspace / Path(test.path)

    copy_tree(src=test_sources, dst=workspace)
    with open(Path(workspace) / "WORKSPACE", mode="wt", encoding="utf-8") as ws_file:
        ws_file.write(WORKSPACE_TEMPLATE.format(dwyu_repo=current_workspace))

    # create report file as input for the applying fixes script
    cmd = ["bazel"]
    if startup_args:
        cmd.extend(startup_args)
    cmd.extend(["build", "--aspects=//:aspect.bzl%dwyu_default_aspect", "--output_groups=cc_dwyu_output"])
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(test.target)
    # Detecting problems causes a red build, thus don't check results
    if verbose:
        sb.run(cmd, cwd=workspace, check=False)
    else:
        sb.run(cmd, cwd=workspace, stdout=sb.PIPE, stderr=sb.PIPE, check=False)


def apply_automatic_fix(workspace: Path, extra_args: List[str], verbose: bool) -> None:
    cmd = ["bazel", "run", "@depend_on_what_you_use//:apply_fixes", "--", f"--workspace={workspace}"]
    if extra_args:
        cmd.extend(extra_args)
    if verbose:
        sb.run(cmd, check=True)
    else:
        sb.run(cmd, stdout=sb.PIPE, stderr=sb.PIPE, check=True)


def query_test_target_dependencies(workspace: Path, target: str, verbose: bool) -> Set["str"]:
    process = sb.run(
        ["bazel", "query", f"labels(deps, {target})"],
        cwd=workspace,
        check=True,
        encoding="utf-8",
        stdout=sb.PIPE,
        stderr=sb.PIPE,
    )
    if verbose:
        print(process.stdout)
    return {dep for dep in process.stdout.split("\n") if dep}


def execute_test(test: TestCase, verbose: bool) -> Result:
    print(f">>> Executing '{test.name}'")

    result = Result(test=test.name)
    with tempfile.TemporaryDirectory() as test_workspace:
        try:
            setup_test_workspace(
                test=test,
                workspace=test_workspace,
                startup_args=test.dwyu_extra_startup_args,
                extra_args=test.dwyu_extra_args,
                verbose=verbose,
            )
            apply_automatic_fix(workspace=test_workspace, extra_args=test.apply_fixes_extra_args, verbose=verbose)

            deps_after_fix = query_test_target_dependencies(
                workspace=test_workspace, target=test.target, verbose=verbose
            )
            expected_deps = set(test.expected_deps)
            if expected_deps != deps_after_fix:
                result.error = (
                    f"Unexpected dependencies: {deps_after_fix}" + "\n" + f"               Expected: {expected_deps}"
                )

        # pylint: disable=broad-except
        except Exception as ex:
            if test.expected_exception:
                if test.expected_exception not in str(ex):
                    result.error = f"Unexpected Exception description: {ex}"
            else:
                result.error = f"Exception: {ex}"

        # Make sure the bazel cache dir is no swamped with dead test workspaces
        sb.run(
            ["bazel", "clean", "--expunge"],
            cwd=test_workspace,
            stdout=sb.PIPE,
            stderr=sb.PIPE,
            check=True,
        )

    if not result.is_success():
        print(result.error)
    status = "OK" if result.is_success() else "FAILURE"
    print(f"<<< {status}\n")

    return result


def main(args, test_cases: List[TestCase]) -> int:
    failed_tests = []
    for test in test_cases:
        if args.test and not test.name in args.test:
            continue

        result = execute_test(test=test, verbose=args.verbose)
        if not result.is_success():
            failed_tests.append(result)

    status = "FAILURE" if failed_tests else "SUCCESS"
    print(f"Testing automatic fixes: {status}")
    if failed_tests:
        print("\nFailed tests:")
        print("\n".join(f"- '{t.test}'" for t in failed_tests))
        return 1

    return 0
