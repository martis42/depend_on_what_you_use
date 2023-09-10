from collections import defaultdict
from dataclasses import dataclass, field
from json import dumps
from typing import DefaultDict, List

from src.analyze_includes.parse_source import Include


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
