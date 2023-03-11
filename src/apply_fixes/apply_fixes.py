import json
import logging
import subprocess
import sys
from os import environ
from pathlib import Path
from typing import Any, Dict, List

from src.apply_fixes.buildozer_executor import BuildozerExecutor

logging.basicConfig(format="%(message)s", level=logging.INFO)

# Bazel sets this environment for 'bazel run' to document the workspace root
WORKSPACE_ENV_VAR = "BUILD_WORKSPACE_DIRECTORY"


class RequestedFixes:
    def __init__(self, main_args: Any) -> None:
        self.remove_unused_deps = main_args.fix_unused_deps or main_args.fix_all
        self.move_private_deps_to_implementation_deps = main_args.fix_deps_which_should_be_private or main_args.fix_all
        self.add_missing_deps = main_args.fix_missing_deps or main_args.fix_all


def execute_and_capture(cmd: List[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    logging.debug(f"Executing command: {cmd}")
    return subprocess.run(cmd, cwd=cwd, check=check, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def get_workspace(main_args: Any) -> Path:
    if main_args.workspace:
        return Path(main_args.workspace)

    workspace_root = environ.get(WORKSPACE_ENV_VAR)
    if not workspace_root:
        print(
            "ERROR:"
            f" No workspace was explicitly provided and environment variable '{WORKSPACE_ENV_VAR}' is not available."
        )
    return Path(workspace_root)


def get_bazel_bin_dir(main_args: Any, workspace_root: Path) -> Path:
    if main_args.bazel_bin:
        return Path(main_args.bazel_bin)

    if main_args.use_bazel_info:
        process = execute_and_capture(
            cmd=["bazel", "info", f"--compilation_mode={main_args.use_bazel_info}", "bazel-bin"], cwd=workspace_root
        )
        return Path(process.stdout.strip())

    bazel_bin_link = workspace_root / "bazel-bin"
    if not bazel_bin_link.is_symlink():
        print(f"ERROR: convenience symlink '{bazel_bin_link}' does not exist or is not a symlink.")
        sys.exit(1)
    return bazel_bin_link.resolve()


def gather_reports(bazel_bin: Path) -> List[Path]:
    return list(bazel_bin.glob("**/*_dwyu_report.json"))


def get_file_name(include: str) -> str:
    return include.split("/")[-1]


def target_to_file(dep: str) -> str:
    """Extract the file name from a Bazel target label"""
    tmp = dep.split(":")[-1]
    return get_file_name(tmp)


def target_to_package(dep: str) -> str:
    return dep.split(":")[0]


def search_missing_deps(workspace: Path, target: str, includes_without_direct_dep: Dict[str, List[str]]) -> List[str]:
    discover_files_process = execute_and_capture(
        cmd=["bazel", "query", "--noimplicit_deps", f'kind("file", deps({target}) except deps({target}, 1))'],
        cwd=workspace,
    )
    discovered_dependencies = []
    files = [line for line in discover_files_process.stdout.splitlines()]

    all_invalid_includes = []
    for _, includes in includes_without_direct_dep.items():
        all_invalid_includes.extend(includes)

    for include in all_invalid_includes:
        include_file = get_file_name(include)
        sources_for_include = [file for file in files if target_to_file(file) == include_file]
        if not sources_for_include:
            logging.warning(
                f"Could not find a file matching invalid include '{include}' in the transitive dependencies of target '{target}'"
            )
            continue

        possible_deps = []
        for file in sources_for_include:
            pkg = target_to_package(file)
            header_deps_process = execute_and_capture(
                cmd=["bazel", "query", f"attr('hdrs', {include_file}, {pkg}:all)"], cwd=workspace
            )
            possible_deps.extend(header_deps_process.stdout.splitlines())

        if not possible_deps:
            logging.warning(
                f"""
Could not find a proper dependency for invalid include '{include}' of target '{target}'.
Is the header file maybe wrongly part of the 'srcs' attribute instead of 'hdrs' in the library which should provide the header?
                """.strip()
            )
            continue

        if len(possible_deps) > 1:
            logging.warning(
                f"""
Found multiple targets which potentially can provide include '{include}' of target '{target}'.
Please fix this manually. Candidates which have been discovered:
                """.strip()
            )
            logging.warning("\n".join(f"- {dep}" for dep in possible_deps))
            continue

        discovered_dependencies.append(possible_deps[0])

    return discovered_dependencies


def add_discovered_deps(
    discovered_public_deps: List[str],
    discovered_private_deps: List[str],
    target: str,
    buildozer: BuildozerExecutor,
    use_implementation_deps: bool,
) -> None:
    add_to_deps = discovered_public_deps
    add_to_implementation_deps = []
    if use_implementation_deps:
        for dep in discovered_private_deps:
            if dep not in add_to_deps:
                add_to_implementation_deps.append(dep)
    else:
        add_to_deps.extend(discovered_private_deps)

    if add_to_deps:
        buildozer.execute(task=f"add deps {' '.join(list(set(add_to_deps)))}", target=target)
    if add_to_implementation_deps:
        buildozer.execute(
            task=f"add implementation_deps {' '.join(list(set(add_to_implementation_deps)))}", target=target
        )


def perform_fixes(buildozer: BuildozerExecutor, workspace: Path, report: Path, requested_fixes: RequestedFixes) -> None:
    with open(report, encoding="utf-8") as report_in:
        content = json.load(report_in)
        target = content["analyzed_target"]

        if requested_fixes.remove_unused_deps:
            unused_public_deps = content["unused_public_deps"]
            if unused_public_deps:
                buildozer.execute(task=f"remove deps {' '.join(unused_public_deps)}", target=target)
            unused_private_deps = content["unused_private_deps"]
            if unused_private_deps:
                buildozer.execute(task=f"remove implementation_deps {' '.join(unused_private_deps)}", target=target)

        if requested_fixes.move_private_deps_to_implementation_deps:
            deps_which_should_be_private = content["deps_which_should_be_private"]
            if deps_which_should_be_private:
                buildozer.execute(
                    task=f"move deps implementation_deps {' '.join(deps_which_should_be_private)}", target=target
                )

        if requested_fixes.add_missing_deps:
            invalid_public_includes = content["public_includes_without_dep"]
            invalid_private_includes = content["private_includes_without_dep"]
            use_implementation_deps = content["use_implementation_deps"]
            discovered_public_deps = []
            discovered_private_deps = []
            if invalid_public_includes:
                discovered_public_deps = search_missing_deps(
                    workspace=workspace, target=target, includes_without_direct_dep=invalid_public_includes
                )
            if invalid_private_includes:
                discovered_private_deps = search_missing_deps(
                    workspace=workspace, target=target, includes_without_direct_dep=invalid_private_includes
                )
            add_discovered_deps(
                discovered_public_deps=discovered_public_deps,
                discovered_private_deps=discovered_private_deps,
                target=target,
                buildozer=buildozer,
                use_implementation_deps=use_implementation_deps,
            )


def main(args: Any) -> int:
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    buildozer = args.buildozer if args.buildozer else "buildozer"

    workspace = get_workspace(args)
    logging.debug(f"Workspace: '{workspace}'")

    bin_dir = get_bazel_bin_dir(main_args=args, workspace_root=workspace)
    logging.debug(f"Bazel-bin directory: '{bin_dir}'")

    reports = gather_reports(bin_dir)
    if not reports:
        logging.error(
            """
ERROR: Did not find any DWYU report files.
Did you forget to run DWYU beforehand?
By default this tool looks for DWYU report files in the output directory for a 'fastbuild' DWYU execution. If you want
to use another output directory, have a look at the apply_fixes CLI options via '--help'.
        """.strip()
        )
        return 1

    buildozer_executor = BuildozerExecutor(
        buildozer=buildozer, buildozer_args=args.buildozer_args, workspace=workspace, dry=args.dry_run
    )
    for report in reports:
        logging.debug(f"Processing report file '{report}'")
        perform_fixes(
            workspace=workspace, report=report, buildozer=buildozer_executor, requested_fixes=RequestedFixes(args)
        )
    buildozer_executor.summary.print_summary()

    return 0
