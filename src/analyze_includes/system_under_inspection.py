import json
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List


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

    def __eq__(self, other: UsageStatus) -> bool:
        return self._usage == other

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


class CcTarget:
    """A cc_* rule target and the available information associated with it."""

    def __init__(self, name: str, include_paths: List[IncludePath], header_files: List[HeaderFile]) -> None:
        self.name = name
        self.include_paths = include_paths
        self.header_files = header_files

    def __repr__(self) -> str:
        return f"CcTarget(name='{self.name}', include_paths={self.include_paths}, header_files={self.header_files})"


class SystemUnderInspection:
    """A target whose include statements are analyzed and its dependencies."""

    def __init__(
        self,
        public_deps: List[CcTarget],
        private_deps: List[CcTarget],
        target_under_inspection: CcTarget,
        compile_flags: List[str],
    ) -> None:
        # Dependencies which are available to downstream dependencies of the target under inspection
        self.public_deps = public_deps
        # Dependencies which are NOT available to downstream dependencies of the target under inspection
        self.private_deps = private_deps
        # Target under inspection
        self.target_under_inspection = target_under_inspection
        # Compile flags for this target
        self.compile_flags = compile_flags


def _make_cc_target(info: Dict) -> CcTarget:
    dep = CcTarget(
        name=info["target"],
        include_paths=[],
        header_files=[HeaderFile(path=header_file) for header_file in info["header_files"]],
    )
    for hdr in info["include_paths"]:
        dep.include_paths.append(IncludePath(hdr))
    return dep


def _extract_preprocessing_flags(compile_flags: List[str]) -> List[str]:
    compile_flags = iter(compile_flags)

    result = []
    for flag in compile_flags:
        flag = flag.strip()
        # ["-DFOO"], ["-DFOO=1"], ["-D", "FOO"], ["-D", "FOO=1"] are supported
        if flag.startswith("-D"):
            result.append(flag)
            if flag == "-D":
                result.append(next(compile_flags))
        # ["-UBAR"], ["-U", "BAR"] are supported
        elif flag.startswith("-U"):
            result.append(flag)
            if flag == "-U":
                result.append(next(compile_flags))
        # FIXME(storypku):
        # Some predefined macros are c++ standard related,
        #   Ref: https://en.cppreference.com/w/cpp/preprocessor/replace#Predefined_macros)
        # However, enabling the -std=X option seems to cause many integration tests fails w/ exception raised:
        #   raise TranslationUnitLoadError("Error parsing translation unit.")
        # So we disable it for now.
        #
        # elif flag.startswith("-std=") or flag.startswith("--std="):
        #    result.append(flag)
    return result


def get_system_under_inspection(allowed_includes_file: Path) -> SystemUnderInspection:
    with open(allowed_includes_file, encoding="utf-8") as fin:
        loaded = json.load(fin)
        return SystemUnderInspection(
            public_deps=[_make_cc_target(dep) for dep in loaded["public_deps"]],
            private_deps=[_make_cc_target(dep) for dep in loaded["private_deps"]],
            target_under_inspection=_make_cc_target(loaded["self"]),
            compile_flags=_extract_preprocessing_flags(loaded["compile_flags"]),
        )
