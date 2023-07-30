import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import List


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


class HeaderFile:
    def __init__(self, path: str) -> None:
        self.path = path
        self.usage = UsageStatusTracker()

    def __repr__(self) -> str:
        return f"HeaderFile(path='{self.path}', usage='{self.usage}')"


class IncludePath:
    def __init__(self, path: str) -> None:
        self.path = path
        self.usage = UsageStatusTracker()

    def __repr__(self) -> str:
        return f"IncludePath(path='{self.path}', usage='{self.usage}')"


@dataclass
class CcTarget:
    """A cc_* rule target and the available information associated with it."""

    name: str
    include_paths: List[IncludePath]
    header_files: List[HeaderFile]

    def __repr__(self) -> str:
        return f"CcTarget(name='{self.name}', include_paths={self.include_paths}, header_files={self.header_files})"


@dataclass
class SystemUnderInspection:
    """A target whose include statements are analyzed and its dependencies."""

    # Dependencies which are available to downstream dependencies of the target under inspection
    deps: List[CcTarget]
    # Dependencies which are NOT available to downstream dependencies of the target under inspection. Exists only for
    # cc_library targets
    implementation_deps: List[CcTarget]
    # Defines influencing the preprocessor
    defines: List[str]
    # Target under inspection
    target_under_inspection: CcTarget


def _make_cc_target(target_file: Path) -> CcTarget:
    with open(target_file, encoding="utf-8") as target:
        target_info = json.load(target)
        cc_target = CcTarget(
            name=target_info["target"],
            include_paths=[],
            header_files=[HeaderFile(path=file) for file in target_info["header_files"]],
        )
        for include_path in target_info["include_paths"]:
            cc_target.include_paths.append(IncludePath(include_path))
        return cc_target


def _cc_targets_from_deps(deps: List[Path]) -> List[CcTarget]:
    return [_make_cc_target(dep) for dep in deps]


def get_system_under_inspection(
    target_under_inspection: Path, deps: List[Path], implementation_deps: List[Path]
) -> SystemUnderInspection:
    with open(target_under_inspection, encoding="utf-8") as target:
        target_info = json.load(target)
        return SystemUnderInspection(
            deps=_cc_targets_from_deps(deps),
            implementation_deps=_cc_targets_from_deps(implementation_deps),
            defines=target_info["defines"],
            target_under_inspection=_make_cc_target(target_under_inspection),
        )
