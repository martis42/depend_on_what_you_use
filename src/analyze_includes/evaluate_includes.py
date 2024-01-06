from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from src.analyze_includes.result import Result
from src.analyze_includes.system_under_inspection import (
    CcTarget,
    SystemUnderInspection,
    UsageStatus,
)

if TYPE_CHECKING:
    from src.analyze_includes.parse_source import Include


def does_include_match_available_files(
    include_statement: str, include_paths: list[str], header_files: list[str]
) -> bool:
    for header in header_files:
        for inc in include_paths:
            possible_file = inc + "/" + include_statement if inc else include_statement
            if possible_file == header:
                return True
    return False


def _include_resolves_to_any_file(included_path: Path, files: list[str]) -> bool:
    return any(included_path == Path(file).resolve() for file in files)


def _is_relative_include(
    target_under_inspection: CcTarget,
    include: Include,
    dependencies: list[CcTarget],
    include_paths: list[str],
    usage: UsageStatus,
) -> bool:
    roots_for_relative_includes = [Path(root) for root in [str(include.file.parent), *include_paths]]
    for root in roots_for_relative_includes:
        path_matching_include_statement = (root / include.include).resolve()

        # Relative include to target under inspection
        if _include_resolves_to_any_file(
            included_path=path_matching_include_statement, files=target_under_inspection.header_files
        ):
            return True

        # Relative include to dependency
        for dep in dependencies:
            if _include_resolves_to_any_file(included_path=path_matching_include_statement, files=dep.header_files):
                dep.usage.update(usage)
                return True

    return False


def _check_for_invalid_includes(
    includes: list[Include],
    dependencies: list[CcTarget],
    usage: UsageStatus,
    target_under_inspection: CcTarget,
    include_paths: list[str],
) -> list[Include]:
    invalid_includes = []

    for inc in includes:
        legal_include = False
        for dep in dependencies:
            if does_include_match_available_files(
                include_statement=inc.include,
                include_paths=include_paths,
                header_files=dep.header_files,
            ):
                legal_include = True
                dep.usage.update(usage)
                break
        if not legal_include:
            # Might be a file from the target under inspection
            legal_include = does_include_match_available_files(
                include_statement=inc.include,
                include_paths=include_paths,
                header_files=target_under_inspection.header_files,
            )
        if not legal_include:
            # Might be a relative include
            legal_include = _is_relative_include(
                target_under_inspection=target_under_inspection,
                include=inc,
                dependencies=dependencies,
                include_paths=include_paths,
                usage=usage,
            )
        if not legal_include:
            invalid_includes.append(inc)

    return invalid_includes


def _check_for_unused_dependencies(dependencies: list[CcTarget]) -> list[str]:
    return [dep.name for dep in dependencies if not dep.usage.is_used()]


def _check_for_public_deps_which_should_be_private(dependencies: SystemUnderInspection) -> list[str]:
    return [dep.name for dep in dependencies.deps if dep.usage.usage == UsageStatus.PRIVATE]


def _filter_empty_dependencies(system_under_inspection: SystemUnderInspection) -> SystemUnderInspection:
    """
    Some dependencies contain no headers and provide only libraries to link against. Since our analysis is based on
    includes we are not interested in those and throw them away to prevent them raising findings regarding unused
    dependencies.
    """
    return SystemUnderInspection(
        target_under_inspection=system_under_inspection.target_under_inspection,
        deps=[dep for dep in system_under_inspection.deps if dep.header_files],
        impl_deps=[dep for dep in system_under_inspection.impl_deps if dep.header_files],
        include_paths=system_under_inspection.include_paths,
        defines=system_under_inspection.defines,
    )


def evaluate_includes(
    public_includes: list[Include],
    private_includes: list[Include],
    system_under_inspection: SystemUnderInspection,
    ensure_private_deps: bool,
) -> Result:
    result = Result(system_under_inspection.target_under_inspection.name)
    system_under_inspection = _filter_empty_dependencies(system_under_inspection)

    result.public_includes_without_dep = _check_for_invalid_includes(
        includes=public_includes,
        dependencies=system_under_inspection.deps,
        usage=UsageStatus.PUBLIC,
        target_under_inspection=system_under_inspection.target_under_inspection,
        include_paths=system_under_inspection.include_paths,
    )
    result.private_includes_without_dep = _check_for_invalid_includes(
        includes=private_includes,
        dependencies=system_under_inspection.deps + system_under_inspection.impl_deps,
        usage=UsageStatus.PRIVATE,
        target_under_inspection=system_under_inspection.target_under_inspection,
        include_paths=system_under_inspection.include_paths,
    )

    result.unused_deps = _check_for_unused_dependencies(system_under_inspection.deps)
    result.unused_impl_deps = _check_for_unused_dependencies(system_under_inspection.impl_deps)

    if ensure_private_deps:
        result.deps_which_should_be_private = _check_for_public_deps_which_should_be_private(system_under_inspection)
        result.use_impl_deps = True

    return result
