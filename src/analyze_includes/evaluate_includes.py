from collections import defaultdict
from dataclasses import dataclass, field
from json import dumps
from pathlib import Path
from typing import List

from src.analyze_includes.get_dependencies import (
    AvailableDependencies,
    AvailableDependency,
    AvailableInclude,
    IncludeUsage,
)
from src.analyze_includes.parse_source import Include


@dataclass
class Result:
    target: str
    invalid_includes: List[Include] = field(default_factory=list)
    unused_deps: List[str] = field(default_factory=list)
    deps_which_should_be_private: List[str] = field(default_factory=list)

    def is_ok(self) -> bool:
        return (
            len(self.invalid_includes) == 0
            and len(self.unused_deps) == 0
            and len(self.deps_which_should_be_private) == 0
        )

    def to_str(self) -> str:
        msg = f"DWYU analyzing: '{self.target}'\n\n"
        if self.is_ok():
            msg += "Result: SUCCESS"
            return self._framed_msg(msg)

        msg += "Result: FAILURE\n"
        if self.invalid_includes:
            msg += "\nIncludes which are not available from the direct dependencies:\n"
            msg += "\n".join(f"  {inc}" for inc in self.invalid_includes)
        if self.unused_deps:
            msg += "\nUnused dependencies (none of their headers are referenced):\n"
            msg += "\n".join(f"  Dependency='{dep}'" for dep in self.unused_deps)
        if self.deps_which_should_be_private:
            msg += "\nPublic dependencies which are used only in private code:\n"
            msg += "\n".join(f"  Dependency='{dep}'" for dep in self.deps_which_should_be_private)
        return self._framed_msg(msg)

    def to_json(self) -> str:
        invalid_includes_mapping = defaultdict(list)
        for x in self.invalid_includes:
            invalid_includes_mapping[str(x.file)].append(x.include)
        content = {
            "analyzed_target": self.target,
            "invalid_includes": invalid_includes_mapping,
            "unused_dependencies": self.unused_deps,
            "deps_which_should_be_private": self.deps_which_should_be_private,
        }
        return dumps(content, indent=2) + "\n"

    @staticmethod
    def _framed_msg(msg: str) -> str:
        """Put a msg vertically between 2 borders"""
        border = 80 * "="
        return border + "\n" + msg + "\n" + border


def _check_for_invalid_includes_impl(
    includes: List[Include],
    own_headers: List[AvailableInclude],
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
            legal = any(inc.include == sh.hdr for sh in own_headers)
        if not legal:
            # Might be a file from the target under inspection with a relative include
            curr_dir = inc.file.parent
            for source in own_headers:
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
        own_headers=dependencies.own_hdrs,
        dependencies=dependencies.public,
        usage=IncludeUsage.PUBLIC,
    )
    invalid_includes.extend(
        _check_for_invalid_includes_impl(
            includes=private_includes,
            own_headers=dependencies.own_hdrs,
            dependencies=dependencies.public + dependencies.private,
            usage=IncludeUsage.PRIVATE,
        )
    )
    return invalid_includes


def _check_for_unused_dependencies_impl(dependencies: List[AvailableDependency]) -> List[str]:
    return [dep.name for dep in dependencies if not any(hdr.used != IncludeUsage.NONE for hdr in dep.hdrs)]


def _check_for_unused_dependencies(dependencies: AvailableDependencies) -> List[str]:
    unused_public_deps = _check_for_unused_dependencies_impl(dependencies.public)
    unused_private_deps = _check_for_unused_dependencies_impl(dependencies.private)
    return unused_public_deps + unused_private_deps


def _check_for_public_deps_which_should_be_private(dependencies: AvailableDependencies) -> List[str]:
    should_be_private = []
    for dep in dependencies.public:
        if all(hdr.used in (IncludeUsage.NONE, IncludeUsage.PRIVATE) for hdr in dep.hdrs) and any(
            hdr.used != IncludeUsage.NONE for hdr in dep.hdrs
        ):
            should_be_private.append(dep.name)
    return should_be_private


def _filter_empty_dependencies(deps: AvailableDependencies) -> AvailableDependencies:
    """
    Some dependencies contain no headers and provide only libraries to link against. Since our analysis is based on
    includes we are not interested in those and throw them away to prevent them raising findings regarding unused
    dependencies.
    """
    return AvailableDependencies(
        own_hdrs=deps.own_hdrs,
        public=[pub for pub in deps.public if pub.hdrs],
        private=[pri for pri in deps.private if pri.hdrs],
    )


def evaluate_includes(
    target: str,
    public_includes: List[Include],
    private_includes: List[Include],
    dependencies: AvailableDependencies,
    ensure_private_deps: bool,
) -> Result:
    result = Result(target)
    dependencies = _filter_empty_dependencies(dependencies)

    result.invalid_includes = _check_for_invalid_includes(
        public_includes=public_includes, private_includes=private_includes, dependencies=dependencies
    )
    result.unused_deps = _check_for_unused_dependencies(dependencies)
    if ensure_private_deps:
        result.deps_which_should_be_private = _check_for_public_deps_which_should_be_private(dependencies)

    return result
