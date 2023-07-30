from collections import defaultdict
from dataclasses import dataclass, field
from json import dumps
from pathlib import Path
from typing import DefaultDict, List

from src.analyze_includes.parse_source import Include
from src.analyze_includes.system_under_inspection import (
    CcTarget,
    SystemUnderInspection,
    UsageStatus,
)


@dataclass
class Result:
    target: str
    public_includes_without_dep: List[Include] = field(default_factory=list)
    private_includes_without_dep: List[Include] = field(default_factory=list)
    unused_deps: List[str] = field(default_factory=list)
    unused_implementation_deps: List[str] = field(default_factory=list)
    deps_which_should_be_private: List[str] = field(default_factory=list)
    use_implementation_deps: bool = False

    def is_ok(self) -> bool:
        return (
            len(self.public_includes_without_dep) == 0
            and len(self.private_includes_without_dep) == 0
            and len(self.unused_deps) == 0
            and len(self.unused_implementation_deps) == 0
            and len(self.deps_which_should_be_private) == 0
        )

    def to_str(self) -> str:
        msg = f"DWYU analyzing: '{self.target}'\n\n"
        if self.is_ok():
            msg += "Result: SUCCESS"
            return self._framed_msg(msg)

        msg += "Result: FAILURE\n"
        if self.public_includes_without_dep or self.private_includes_without_dep:
            msg += "\nIncludes which are not available from the direct dependencies:\n"
            msg += "\n".join(f"  {inc}" for inc in self.public_includes_without_dep + self.private_includes_without_dep)
        if self.unused_deps:
            msg += "\nUnused dependencies in 'deps' (none of their headers are referenced):\n"
            msg += "\n".join(f"  Dependency='{dep}'" for dep in self.unused_deps)
        if self.unused_implementation_deps:
            msg += "\nUnused dependencies in 'implementation_deps' (none of their headers are referenced):\n"
            msg += "\n".join(f"  Dependency='{dep}'" for dep in self.unused_implementation_deps)
        if self.deps_which_should_be_private:
            msg += "\nPublic dependencies which are used only in private code:\n"
            msg += "\n".join(f"  Dependency='{dep}'" for dep in self.deps_which_should_be_private)
        return self._framed_msg(msg)

    def to_json(self) -> str:
        content = {
            "analyzed_target": self.target,
            "public_includes_without_dep": self._make_includes_map(self.public_includes_without_dep),
            "private_includes_without_dep": self._make_includes_map(self.private_includes_without_dep),
            "unused_deps": self.unused_deps,
            "unused_implementation_deps": self.unused_implementation_deps,
            "deps_which_should_be_private": self.deps_which_should_be_private,
            "use_implementation_deps": self.use_implementation_deps,
        }
        return dumps(content, indent=2) + "\n"

    @staticmethod
    def _make_includes_map(includes: List[Include]) -> DefaultDict[str, List[str]]:
        includes_mapping = defaultdict(list)
        for inc in includes:
            includes_mapping[str(inc.file)].append(inc.include)
        return includes_mapping

    @staticmethod
    def _framed_msg(msg: str) -> str:
        """Put a msg vertically between 2 borders"""
        border = 80 * "="
        return border + "\n" + msg + "\n" + border


def _check_for_invalid_includes(
    includes: List[Include],
    dependencies: List[CcTarget],
    usage: UsageStatus,
    target_under_inspection: CcTarget,
) -> List[Include]:
    invalid_includes = []

    all_header_files = []
    all_header_files.extend(target_under_inspection.header_files)
    for dep in dependencies:
        all_header_files.extend(dep.header_files)

    for inc in includes:
        legal = False
        for dep in dependencies:
            if legal:
                break
            for dep_hdr in dep.include_paths:
                if inc.include == dep_hdr.path:
                    legal = True
                    dep_hdr.usage.update(usage)
                    break
        if not legal:
            # Might be a file from the target under inspection
            legal = any(inc.include == sh.path for sh in target_under_inspection.include_paths)
        if not legal:
            # Might be a relative include
            curr_dir = inc.file.parent
            for hf in all_header_files:
                path_matching_include_statement = (curr_dir / inc.include).resolve()
                if path_matching_include_statement == Path(hf.path).resolve():
                    legal = True
                    hf.usage.update(usage)
                    break
        if not legal:
            invalid_includes.append(inc)
    return invalid_includes


def _check_for_unused_dependencies(dependencies: List[CcTarget]) -> List[str]:
    unused_deps = []
    for dep in dependencies:
        if all(not hdr.usage.is_used() for hdr in dep.include_paths) and all(
            not hdr.usage.is_used() for hdr in dep.header_files
        ):
            unused_deps.append(dep.name)
    return unused_deps


def _check_for_public_deps_which_should_be_private(dependencies: SystemUnderInspection) -> List[str]:
    should_be_private = []
    for dep in dependencies.deps:
        if all(hdr.usage.usage in (UsageStatus.NONE, UsageStatus.PRIVATE) for hdr in dep.include_paths) and any(
            hdr.usage.is_used() for hdr in dep.include_paths
        ):
            should_be_private.append(dep.name)
    return should_be_private


def _filter_empty_dependencies(system_under_inspection: SystemUnderInspection) -> SystemUnderInspection:
    """
    Some dependencies contain no headers and provide only libraries to link against. Since our analysis is based on
    includes we are not interested in those and throw them away to prevent them raising findings regarding unused
    dependencies.
    """
    return SystemUnderInspection(
        deps=[dep for dep in system_under_inspection.deps if dep.include_paths],
        implementation_deps=[dep for dep in system_under_inspection.implementation_deps if dep.include_paths],
        defines=system_under_inspection.defines,
        target_under_inspection=system_under_inspection.target_under_inspection,
    )


def evaluate_includes(
    public_includes: List[Include],
    private_includes: List[Include],
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
    )
    result.private_includes_without_dep = _check_for_invalid_includes(
        includes=private_includes,
        dependencies=system_under_inspection.deps + system_under_inspection.implementation_deps,
        usage=UsageStatus.PRIVATE,
        target_under_inspection=system_under_inspection.target_under_inspection,
    )

    result.unused_deps = _check_for_unused_dependencies(system_under_inspection.deps)
    result.unused_implementation_deps = _check_for_unused_dependencies(system_under_inspection.implementation_deps)

    if ensure_private_deps:
        result.deps_which_should_be_private = _check_for_public_deps_which_should_be_private(system_under_inspection)
        result.use_implementation_deps = True

    return result
