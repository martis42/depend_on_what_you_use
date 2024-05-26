from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from json import dumps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from src.analyze_includes.parse_source import Include


@dataclass
class Result:
    target: str
    report: Path | None = None
    use_impl_deps: bool = False

    public_includes_without_dep: list[Include] = field(default_factory=list)
    private_includes_without_dep: list[Include] = field(default_factory=list)
    unused_deps: list[str] = field(default_factory=list)
    unused_impl_deps: list[str] = field(default_factory=list)
    deps_which_should_be_private: list[str] = field(default_factory=list)

    def is_ok(self) -> bool:
        return (
            len(self.public_includes_without_dep) == 0
            and len(self.private_includes_without_dep) == 0
            and len(self.unused_deps) == 0
            and len(self.unused_impl_deps) == 0
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
        if self.unused_impl_deps:
            msg += "\nUnused dependencies in 'implementation_deps' (none of their headers are referenced):\n"
            msg += "\n".join(f"  Dependency='{dep}'" for dep in self.unused_impl_deps)
        if self.deps_which_should_be_private:
            msg += "\nPublic dependencies which are used only in private code:\n"
            msg += "\n".join(f"  Dependency='{dep}'" for dep in self.deps_which_should_be_private)

        msg += f"\n\nDWYU Report: {self.report}"

        return self._framed_msg(msg)

    def to_json(self) -> str:
        content = {
            "analyzed_target": self.target,
            "public_includes_without_dep": self._make_includes_map(self.public_includes_without_dep),
            "private_includes_without_dep": self._make_includes_map(self.private_includes_without_dep),
            "unused_deps": self.unused_deps,
            "unused_implementation_deps": self.unused_impl_deps,
            "deps_which_should_be_private": self.deps_which_should_be_private,
            "use_implementation_deps": self.use_impl_deps,
        }
        return dumps(content, indent=2) + "\n"

    @staticmethod
    def _make_includes_map(includes: list[Include]) -> defaultdict[str, list[str]]:
        includes_mapping = defaultdict(list)
        for inc in includes:
            includes_mapping[str(inc.file)].append(inc.include)
        return includes_mapping

    @staticmethod
    def _framed_msg(msg: str) -> str:
        """Put a message between 2 horizontal borders"""
        border = 80 * "="
        return border + "\n" + msg + "\n" + border
