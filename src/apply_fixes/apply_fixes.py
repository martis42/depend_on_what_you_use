import json
import logging
import subprocess
import sys
from os import environ
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(format="%(message)s", level=logging.INFO)

# Bazel sets this environment for 'bazel run' to document the workspace root
WORKSPACE_ENV_VAR = "BUILD_WORKSPACE_DIRECTORY"


class Summary:
    def __init__(self) -> None:
        self.succesful_fixes = []
        self.failed_fixes = []
        self.fixes_without_effect = []

    def add_command(self, cmd: List[str], buildozer_result: int) -> None:
        if buildozer_result == 0:
            self.succesful_fixes.append(cmd)
        elif buildozer_result == 2:
            self.failed_fixes.append(cmd)
        elif buildozer_result == 3:
            self.fixes_without_effect.append(cmd)
        else:
            raise Exception(
                f"Running buildozer command '{cmd}' failed with the unexpected return code: {buildozer_result}"
            )

    # restricting the type to instances of the own class seems to be not possible with Python 3.6
    def extend(self, other: Any) -> Any:
        self.succesful_fixes.extend(other.succesful_fixes)
        self.failed_fixes.extend(other.failed_fixes)
        self.fixes_without_effect.extend(other.fixes_without_effect)

    def print_summary(self) -> None:
        print(f"\nSuccesful fixes: {len(self.succesful_fixes)}")

        if self.failed_fixes:
            print(
                """
WARNING Some buildozer commands failed!
Common causes for this can be:
- The workspace has changed since the DWYU report files have been generated and thus some targets no longer exist.
- The target which is supposed to be fixed is not written directly in a BUILD file, but created by a macro.

Failed commands:"""
            )
            print("\n".join(f"- {x}" for x in self.failed_fixes))

        if self.fixes_without_effect:
            print(
                """
WARNING Some buildozer commands did not create a change!
Common causes for this can be:
- You are executing the apply fixes script multiple times on the same report file.
- The script is trying to remove an aliased target. DWYU is only aware of the resolved target, which buildozer cannot
  connect to the alias name in the dependency list.

Commands without effect:"""
            )
            print("\n".join(f"- {x}" for x in self.fixes_without_effect))


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
        process = subprocess.run(
            ["bazel", "info", f"--compilation_mode={main_args.use_bazel_info}", "bazel-bin"],
            cwd=workspace_root,
            check=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return Path(process.stdout.strip())

    bazel_bin_link = workspace_root / "bazel-bin"
    if not bazel_bin_link.is_symlink():
        print(f"ERROR: convenience symlink '{bazel_bin_link}' does not exist or is not a symlink.")
        sys.exit(1)
    return bazel_bin_link.resolve()


def gather_reports(bazel_bin: Path) -> List[Path]:
    return list(bazel_bin.glob("**/*_dwyu_report.json"))


def make_base_cmd(buildozer: str, dry: bool, buildozer_args: List[str]) -> List[str]:
    cmd = [buildozer]
    if buildozer_args:
        cmd.extend(buildozer_args)
    if dry:
        cmd.append("-stdout")
    return cmd


def execute_buildozer(cmd: List[str], workspace: Path, summary: Summary, dry: bool) -> None:
    logging.log(logging.INFO if dry else logging.DEBUG, f"Executing buildozer command: {cmd}")
    process = subprocess.run(cmd, cwd=workspace, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    summary.add_command(cmd=cmd, buildozer_result=process.returncode)


def get_file_name(include: str) -> str:
    return include.split("/")[-1]


def dep_to_file(dep: str) -> str:
    tmp = dep.split(":")[-1]
    return get_file_name(tmp)


def dep_to_package(dep: str) -> str:
    return dep.split(":")[0]


def search_missing_deps(workspace: Path, target: str, includes_without_direct_dep: Dict[str, List[str]]) -> List[str]:
    process = subprocess.run(
        ["bazel", "query", "--noimplicit_deps", f'kind("file", deps({target}) except deps({target}, 1))'],
        cwd=workspace,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

    discovered_dependencies = []

    files = [line for line in process.stdout.splitlines()]

    all_invalid_includes = []
    for _, includes in includes_without_direct_dep.items():
        all_invalid_includes.extend(includes)

    for include in all_invalid_includes:
        include_file = get_file_name(include)
        sources_for_include = [file for file in files if dep_to_file(file) == include_file]
        if not sources_for_include:
            logging.warning(
                f"Could not find a file matching invalid include '{include}' in the transitive dependencies of target '{target}'"
            )
            continue

        possible_deps = []
        for x in sources_for_include:
            pkg = dep_to_package(x)
            cmd = ["bazel", "query", f"attr('hdrs', {include_file}, {pkg}:all)"]
            process2 = subprocess.run(
                cmd,
                cwd=workspace,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
            )
            possible_deps.extend(process2.stdout.splitlines())

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


def add_deps(
    deps: List[str],
    target: str,
    workspace: Path,
    buildozer_base_cmd: List[str],
    deps_attribute: str,
    summary: Summary,
    dry: bool,
) -> None:
    if deps:
        deps = list(set(deps))
        add_deps_cmd = buildozer_base_cmd + [f"add {deps_attribute} {' '.join(deps)}", target]
        execute_buildozer(cmd=add_deps_cmd, workspace=workspace, summary=summary, dry=dry)


def add_discovered_deps(
    discovered_public_deps: List[str],
    discovered_private_deps: List[str],
    target: str,
    workspace: Path,
    summary: Summary,
    buildozer_base_cmd: List[str],
    use_implementation_deps: bool,
    dry: bool,
) -> None:
    add_to_deps = discovered_public_deps
    add_to_implementation_deps = []
    if use_implementation_deps:
        for dep in discovered_private_deps:
            if dep not in add_to_deps:
                add_to_implementation_deps.append(dep)
    else:
        add_to_deps.extend(discovered_private_deps)

    add_deps(
        deps=add_to_deps,
        target=target,
        workspace=workspace,
        buildozer_base_cmd=buildozer_base_cmd,
        deps_attribute="deps",
        summary=summary,
        dry=dry,
    )
    add_deps(
        deps=add_to_implementation_deps,
        target=target,
        workspace=workspace,
        buildozer_base_cmd=buildozer_base_cmd,
        deps_attribute="implementation_deps",
        summary=summary,
        dry=dry,
    )


def perform_fixes(
    workspace: Path, report: Path, buildozer: str, buildozer_args: List[str], add_missing_deps: bool, dry: bool
) -> Summary:
    summary = Summary()

    with open(report, encoding="utf-8") as report_in:
        content = json.load(report_in)
        target = content["analyzed_target"]
        unused_public_deps = content["unused_public_deps"]
        unused_private_deps = content["unused_private_deps"]
        deps_which_should_be_private = content["deps_which_should_be_private"]

        base_cmd = make_base_cmd(buildozer=buildozer, buildozer_args=buildozer_args, dry=dry)
        if unused_public_deps:
            deps_str = " ".join(unused_public_deps)
            remove_deps = base_cmd + [f"remove deps {deps_str}", target]
            execute_buildozer(cmd=remove_deps, workspace=workspace, summary=summary, dry=dry)
        if unused_private_deps:
            deps_str = " ".join(unused_private_deps)
            remove_deps = base_cmd + [f"remove implementation_deps {deps_str}", target]
            execute_buildozer(cmd=remove_deps, workspace=workspace, summary=summary, dry=dry)
        if deps_which_should_be_private:
            deps_str = " ".join(deps_which_should_be_private)
            move_deps = base_cmd + [f"move deps implementation_deps {deps_str}", target]
            execute_buildozer(cmd=move_deps, workspace=workspace, summary=summary, dry=dry)
        if add_missing_deps:
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
                workspace=workspace,
                summary=summary,
                buildozer_base_cmd=base_cmd,
                use_implementation_deps=use_implementation_deps,
                dry=dry,
            )

    return summary


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
        print("ERROR: Did not find any DWYU report files.")
        print("Did you forget to run DWYU beforehand?")
        print(
            "By default this tool looks for DWYU report files in the output directory for a 'fastbuild' DWYU execution."
            " If you want to use another output directory, have a look at the apply_fixes CLI options via '--help'."
        )
        return 1

    overall_summary = Summary()
    for report in reports:
        logging.debug(f"Processing report file '{report}'")
        summary = perform_fixes(
            workspace=workspace,
            report=report,
            buildozer=buildozer,
            buildozer_args=args.buildozer_args,
            add_missing_deps=args.add_missing_deps,
            dry=args.dry_run,
        )
        overall_summary.extend(summary)

    overall_summary.print_summary()

    return 0
