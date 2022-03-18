from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from src.get_dependencies import (AvailableDependencies, AvailableDependency,
                                  IncludeUsage)
from src.parse_source import Include


@dataclass
class DependencyUtilization:
    """How many percent of headers from a dependency are used in the target under inspection"""

    name: str
    utilization: int


@dataclass
class Result:
    target: str
    invalid_includes: List[Include] = field(default_factory=list)
    unused_deps: List[str] = field(default_factory=list)
    deps_which_should_be_private: List[str] = field(default_factory=list)
    deps_with_low_utilization: List[DependencyUtilization] = field(default_factory=list)

    def is_ok(self) -> bool:
        return (
            len(self.invalid_includes) == 0
            and len(self.unused_deps) == 0
            and len(self.deps_which_should_be_private) == 0
            and len(self.deps_with_low_utilization) == 0
        )

    def to_str(self) -> str:
        msg = f"DWYU analyzing: '{self.target}'\n\n"
        if self.is_ok():
            msg += "Result: SUCCESS"
            return self._framed_msg(msg)
        else:
            msg += "Result: FAILURE\n"
            if self.invalid_includes:
                msg += "\nIncludes which are not available from the direct dependencies:\n"
                msg += "\n".join(f"  {inc}" for inc in self.invalid_includes)
            if self.unused_deps:
                msg += "\nUnused dependencies (none of their headers are referenced):\n"
                msg += "\n".join(f"  Dependency='{dep}'" for dep in self.unused_deps)
            if self.deps_which_should_be_private:
                msg += (
                    "\nPublic dependencies which are only used in private code, move them to 'implementation_deps':\n"
                )
                msg += "\n".join(f"  Dependency='{dep}'" for dep in self.deps_which_should_be_private)
            if self.deps_with_low_utilization:
                msg += "\nDependencies with utilization below the threshold:\n"
                msg += "\n".join(
                    f"  Dependency='{dep.name}', utilization='{dep.utilization}'"
                    for dep in self.deps_with_low_utilization
                )
            return self._framed_msg(msg)

    @staticmethod
    def _framed_msg(msg: str) -> str:
        """Put a msg vertically between 2 borders"""
        border = 80 * "="
        return border + "\n" + msg + "\n" + border


def _check_for_invalid_includes_impl(
    includes: List[Include],
    self: AvailableDependency,
    dependencies: List[AvailableDependency],
    usage: IncludeUsage,
) -> List[str]:
    invalid_includes = []
    for inc in includes:
        legal = False
        for dep in dependencies:
            for dep_hdr in dep.hdrs:
                if inc.include == dep_hdr.hdr:
                    legal = True
                    dep_hdr.update_usage(usage)
                    break
        if not legal:
            # Might be a file from the target under inspection
            legal = any(inc.include == sh.hdr for sh in self.hdrs)
        if not legal:
            # Might be a file from the target under inspection with a relative include
            curr_dir = inc.file.parent
            for source in self.hdrs:
                try:
                    rel_path = Path(source.hdr).relative_to(curr_dir)
                    if rel_path == Path(inc.include):
                        legal = True
                        break
                except ValueError:
                    pass
        if not legal:
            invalid_includes.append(inc)
    return invalid_includes


def _check_for_invalid_includes(
    public_includes: List[Include], private_includes: List[Include], dependencies: AvailableDependencies
) -> List[Include]:
    """Iterate through all include statements and determine if they correspond to an available dependency"""

    invalid_includes = _check_for_invalid_includes_impl(
        includes=public_includes,
        self=dependencies.self,
        dependencies=dependencies.public,
        usage=IncludeUsage.PUBLIC,
    )
    invalid_includes.extend(
        _check_for_invalid_includes_impl(
            includes=private_includes,
            self=dependencies.self,
            dependencies=dependencies.public + dependencies.private,
            usage=IncludeUsage.PRIVATE,
        )
    )
    return invalid_includes


def _check_for_unused_dependencies_impl(dependencies: List[AvailableDependency]) -> List[str]:
    return [dep.name for dep in dependencies if not any((hdr.used != IncludeUsage.NONE for hdr in dep.hdrs))]


def _check_for_unused_dependencies(dependencies: AvailableDependencies) -> List[str]:
    unused_public_deps = _check_for_unused_dependencies_impl(dependencies.public)
    unused_private_deps = _check_for_unused_dependencies_impl(dependencies.private)
    return unused_public_deps + unused_private_deps


def _check_for_public_deps_which_should_be_private(dependencies: AvailableDependencies) -> List[str]:
    should_be_private = []
    for dep in dependencies.public:
        if all((hdr.used in (IncludeUsage.NONE, IncludeUsage.PRIVATE) for hdr in dep.hdrs)) and any(
            hdr.used != IncludeUsage.NONE for hdr in dep.hdrs
        ):
            should_be_private.append(dep.name)
    return should_be_private


def _check_for_deps_whith_low_utilization_impl(
    dependencies: List[AvailableDependency], min_utilization: int
) -> List[DependencyUtilization]:
    lowly_utilized_deps = []
    for dep in dependencies:
        used = sum(hdr.used != IncludeUsage.NONE for hdr in dep.hdrs)
        utilization = int(100 * used / len(dep.hdrs))
        if utilization < min_utilization:
            lowly_utilized_deps.append(DependencyUtilization(name=dep.name, utilization=utilization))
    return lowly_utilized_deps


def _check_for_deps_whith_low_utilization(
    dependencies: AvailableDependencies, min_utilization: int
) -> List[DependencyUtilization]:
    lowly_utilized_deps = _check_for_deps_whith_low_utilization_impl(
        dependencies=dependencies.public, min_utilization=min_utilization
    )
    lowly_utilized_deps.extend(
        _check_for_deps_whith_low_utilization_impl(dependencies=dependencies.private, min_utilization=min_utilization)
    )
    return lowly_utilized_deps


def _filter_empty_dependencies(deps: AvailableDependencies) -> AvailableDependencies:
    """
    Some dependencies contain no headers and provide only libraries to link against. Since our analysis is based on
    includes we are not interested in those and throw them away to prevent them raising findings regarding unused
    dependencies or header utilization.
    """
    return AvailableDependencies(
        self=deps.self,
        public=[pub for pub in deps.public if pub.hdrs],
        private=[pri for pri in deps.private if pri.hdrs],
    )


def evaluate_includes(
    target: str,
    public_includes: List[Include],
    private_includes: List[Include],
    dependencies: AvailableDependencies,
    ensure_private_deps: bool,
    min_dependency_utilization: int,
) -> Result:
    result = Result(target)
    dependencies = _filter_empty_dependencies(dependencies)

    result.invalid_includes = _check_for_invalid_includes(
        public_includes=public_includes, private_includes=private_includes, dependencies=dependencies
    )
    result.unused_deps = _check_for_unused_dependencies(dependencies)
    if ensure_private_deps:
        result.deps_which_should_be_private = _check_for_public_deps_which_should_be_private(dependencies)
    if min_dependency_utilization > 0:
        result.deps_with_low_utilization = _check_for_deps_whith_low_utilization(
            dependencies=dependencies, min_utilization=min_dependency_utilization
        )

    return result
