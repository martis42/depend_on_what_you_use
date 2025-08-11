from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from dwyu.aspect.private.analyze_includes.evaluate_includes import (
    _check_for_public_deps_which_should_be_private,
    _check_for_unused_dependencies,
)
from dwyu.aspect.private.analyze_includes.parse_source import Include
from dwyu.aspect.private.analyze_includes.result import Result
from dwyu.aspect.private.analyze_includes.system_under_inspection import (
    CcTarget,
    UsageStatus,
    _cc_targets_from_deps,
    _make_cc_target,
)


@dataclass
class SystemUnderInspection:
    """A target whose include statements are analyzed and its dependencies."""

    # Target under inspection
    target_under_inspection: CcTarget
    # Dependencies which are available to downstream dependencies of the target under inspection
    deps: list[CcTarget]
    # Dependencies which are not available to downstream dependencies of the target under inspection
    impl_deps: list[CcTarget]


def get_system_under_inspection(
    target_under_inspection: Path, deps: list[Path], impl_deps: list[Path]
) -> SystemUnderInspection:
    return SystemUnderInspection(
        target_under_inspection=_make_cc_target(target_under_inspection),
        deps=_cc_targets_from_deps(deps),
        impl_deps=_cc_targets_from_deps(impl_deps),
    )


def aggregate_preprocessed_includes(
    # preprocessed_includes: list[Path], ignored_includes: IgnoredIncludes
    preprocessed_includes: list[Path],
) -> list[Include]:
    all_includes = []
    for file in preprocessed_includes:
        data = json.loads(file.read_text())
        all_includes.extend([Include(file=Path(data["file"]), include=inc) for inc in data["included_headers"]])

    # return filter_includes(includes=all_includes, ignored_includes=ignored_includes)
    return all_includes


def filter_empty_dependencies(system_under_inspection: SystemUnderInspection) -> SystemUnderInspection:
    """
    Some dependencies contain no headers and provide only libraries to link against. Since our analysis is based on
    includes we are not interested in those and throw them away to prevent them raising findings regarding unused
    dependencies.
    """
    return SystemUnderInspection(
        target_under_inspection=system_under_inspection.target_under_inspection,
        deps=[dep for dep in system_under_inspection.deps if dep.header_files],
        impl_deps=[dep for dep in system_under_inspection.impl_deps if dep.header_files],
    )


def check_for_invalid_includes(
    included_headers: list[Include],
    dependencies: list[CcTarget],
    usage: UsageStatus,
    target_under_inspection: CcTarget,
    toolchain_headers: set[str],
) -> list[Include]:
    invalid_includes = []

    # TODO checks might be more efficient on deps with many files if sets are used
    for inc in included_headers:
        legal_include = False

        if inc.include in toolchain_headers:
            continue

        # First check if the included header is from one of the dependencies
        for dep in dependencies:
            if inc.include in dep.header_files:
                legal_include = True
                dep.usage.update(usage)
                # We cannot break early, as a header might actually be provided by multiple dependencies

        # Header might be from the target under inspection itself
        if not legal_include and inc.include in target_under_inspection.header_files:
            legal_include = True

        if not legal_include:
            invalid_includes.append(inc)

    return invalid_includes


def evaluate_includes(
    public_includes: list[Include],
    private_includes: list[Include],
    system_under_inspection: SystemUnderInspection,
    ensure_private_deps: bool,
    toolchain_headers: set[str],
) -> Result:
    result = Result(system_under_inspection.target_under_inspection.name)
    system_under_inspection = filter_empty_dependencies(system_under_inspection)

    result.public_includes_without_dep = check_for_invalid_includes(
        included_headers=public_includes,
        dependencies=system_under_inspection.deps,
        usage=UsageStatus.PUBLIC,
        target_under_inspection=system_under_inspection.target_under_inspection,
        toolchain_headers=toolchain_headers,
    )
    result.private_includes_without_dep = check_for_invalid_includes(
        included_headers=private_includes,
        dependencies=system_under_inspection.deps + system_under_inspection.impl_deps,
        usage=UsageStatus.PRIVATE,
        target_under_inspection=system_under_inspection.target_under_inspection,
        toolchain_headers=toolchain_headers,
    )

    result.unused_deps = _check_for_unused_dependencies(system_under_inspection.deps)
    result.unused_impl_deps = _check_for_unused_dependencies(system_under_inspection.impl_deps)

    if ensure_private_deps:
        result.deps_which_should_be_private = _check_for_public_deps_which_should_be_private(system_under_inspection)
        result.use_impl_deps = True

    return result
