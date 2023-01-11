from collections import defaultdict
from json import dumps
from pathlib import Path
from typing import Dict, List, Optional

from src.analyze_includes.get_dependencies import (
    AvailableDependencies,
    AvailableDependency,
    AvailableInclude,
    IncludeUsage,
)
from src.analyze_includes.parse_source import Include


class Result:
    def __init__(
        self,
        target: str,
        public_includes_without_dep: Optional[List[Include]] = None,
        private_includes_without_dep: Optional[List[Include]] = None,
        unused_public_deps: Optional[List[str]] = None,
        unused_private_deps: Optional[List[str]] = None,
        deps_which_should_be_private: Optional[List[str]] = None,
    ) -> None:
        self.target = target
        self.public_includes_without_dep = public_includes_without_dep if public_includes_without_dep else []
        self.private_includes_without_dep = private_includes_without_dep if private_includes_without_dep else []
        self.unused_public_deps = unused_public_deps if unused_public_deps else []
        self.unused_private_deps = unused_private_deps if unused_private_deps else []
        self.deps_which_should_be_private = deps_which_should_be_private if deps_which_should_be_private else []

    def is_ok(self) -> bool:
        return (
            len(self.public_includes_without_dep) == 0
            and len(self.private_includes_without_dep) == 0
            and len(self.unused_public_deps) == 0
            and len(self.unused_private_deps) == 0
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
        if self.unused_public_deps:
            msg += "\nUnused dependencies in 'deps' (none of their headers are referenced):\n"
            msg += "\n".join(f"  Dependency='{dep}'" for dep in self.unused_public_deps)
        if self.unused_private_deps:
            msg += "\nUnused dependencies in 'implementation_deps' (none of their headers are referenced):\n"
            msg += "\n".join(f"  Dependency='{dep}'" for dep in self.unused_private_deps)
        if self.deps_which_should_be_private:
            msg += "\nPublic dependencies which are used only in private code:\n"
            msg += "\n".join(f"  Dependency='{dep}'" for dep in self.deps_which_should_be_private)
        return self._framed_msg(msg)

    def to_json(self) -> str:
        content = {
            "analyzed_target": self.target,
            "public_includes_without_dep": self._make_includes_map(self.public_includes_without_dep),
            "private_includes_without_dep": self._make_includes_map(self.private_includes_without_dep),
            "unused_public_deps": self.unused_public_deps,
            "unused_private_deps": self.unused_private_deps,
            "deps_which_should_be_private": self.deps_which_should_be_private,
        }
        return dumps(content, indent=2) + "\n"

    @staticmethod
    def _make_includes_map(includes: List[Include]) -> Dict[str, str]:
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


def _check_for_unused_dependencies(dependencies: List[AvailableDependency]) -> List[str]:
    return [dep.name for dep in dependencies if all(hdr.used == IncludeUsage.NONE for hdr in dep.hdrs)]


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

    result.public_includes_without_dep = _check_for_invalid_includes(
        includes=public_includes,
        own_headers=dependencies.own_hdrs,
        dependencies=dependencies.public,
        usage=IncludeUsage.PUBLIC,
    )
    result.private_includes_without_dep = _check_for_invalid_includes(
        includes=private_includes,
        own_headers=dependencies.own_hdrs,
        dependencies=dependencies.public + dependencies.private,
        usage=IncludeUsage.PRIVATE,
    )

    result.unused_public_deps = _check_for_unused_dependencies(dependencies.public)
    result.unused_private_deps = _check_for_unused_dependencies(dependencies.private)

    if ensure_private_deps:
        result.deps_which_should_be_private = _check_for_public_deps_which_should_be_private(dependencies)

    return result
