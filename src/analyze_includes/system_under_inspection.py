from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


class UsageStatus(Enum):
    """Classification whether a header was used in public or private files"""

    NONE = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    PUBLIC_AND_PRIVATE = auto()


class UsageStatusTracker:
    def __init__(self) -> None:
        self._usage = UsageStatus.NONE

    def update(self, usage_update: UsageStatus) -> None:
        if usage_update == UsageStatus.NONE:
            raise Exception("Resetting the usage is not supported")

        if self._usage == UsageStatus.PUBLIC_AND_PRIVATE:
            return

        if usage_update == UsageStatus.PUBLIC_AND_PRIVATE:
            self._usage = UsageStatus.PUBLIC_AND_PRIVATE
        elif self._usage == UsageStatus.NONE:
            self._usage = usage_update
        elif (self._usage == UsageStatus.PUBLIC and usage_update == UsageStatus.PRIVATE) or (
            self._usage == UsageStatus.PRIVATE and usage_update == UsageStatus.PUBLIC
        ):
            self._usage = UsageStatus.PUBLIC_AND_PRIVATE

    @property
    def usage(self) -> UsageStatus:
        return self._usage

    def is_used(self) -> bool:
        return self._usage != UsageStatus.NONE

    def __repr__(self) -> str:
        return self._usage.name


@dataclass
class CcTarget:
    """A cc_* rule target and the available information associated with it."""

    name: str
    header_files: list[str]
    usage: UsageStatusTracker = field(init=False)

    def __post_init__(self) -> None:
        self.usage = UsageStatusTracker()

    def __repr__(self) -> str:
        return f"CcTarget(name='{self.name}', usage='{self.usage}', header_files={self.header_files})"


@dataclass
class SystemUnderInspection:
    """A target whose include statements are analyzed and its dependencies."""

    # Target under inspection
    target_under_inspection: CcTarget
    # Dependencies which are available to downstream dependencies of the target under inspection
    deps: list[CcTarget]
    # Dependencies which are NOT available to downstream dependencies of the target under inspection. Exists only for
    # cc_library targets
    impl_deps: list[CcTarget]
    # All include paths available to the target under inspection. Combines all kinds of includes.
    include_paths: list[str]
    # Defines influencing the preprocessor
    defines: list[str]


def _make_cc_target(target_file: Path) -> CcTarget:
    with open(target_file, encoding="utf-8") as target:
        target_info = json.load(target)
        cc_target = CcTarget(
            name=target_info["target"],
            header_files=target_info["header_files"],
        )
        return cc_target


def _cc_targets_from_deps(deps: list[Path]) -> list[CcTarget]:
    return [_make_cc_target(dep) for dep in deps]


def _get_include_paths(target_info: dict[str, Any]) -> list[str]:
    """
    '.' represents the workspace root relative to which all paths in a Bazel workspace are defined. Our internal logic
    does however expect an empty string for the "include relative to workspace root" case.
    """

    def replace_dot(paths: list[str]) -> list[str]:
        return ["" if path == "." else path for path in paths]

    return (
        replace_dot(target_info["includes"])
        + replace_dot(target_info["quote_includes"])
        + replace_dot(target_info["system_includes"])
    )


def _get_defines(target_info: dict[str, Any]) -> list[str]:
    """
    Defines with values in BUILD files or the compiler CLI can be specified via '<DEFINE_TOKEN>=<VALUE>'. However, this
    syntax is not valid for the preprocessor, which expects '<DEFINE_TOKEN> <VALUE>'.
    """
    return [define.replace("=", " ") for define in target_info["defines"]]


def get_system_under_inspection(
    target_under_inspection: Path, deps: list[Path], impl_deps: list[Path]
) -> SystemUnderInspection:
    with open(target_under_inspection, encoding="utf-8") as target:
        target_info = json.load(target)
        return SystemUnderInspection(
            target_under_inspection=_make_cc_target(target_under_inspection),
            deps=_cc_targets_from_deps(deps),
            impl_deps=_cc_targets_from_deps(impl_deps),
            include_paths=_get_include_paths(target_info),
            defines=_get_defines(target_info),
        )
