import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List


class IncludeUsage(Enum):
    """Classification whether a header was used in public or private files"""

    NONE = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    PUBLIC_AND_PRIVATE = auto()


@dataclass
class AvailableInclude:
    """Include path provided by a dependency"""

    hdr: str
    used: IncludeUsage = IncludeUsage.NONE

    def update_usage(self, usage: IncludeUsage) -> None:
        if usage == IncludeUsage.NONE:
            raise Exception("Resetting the include usage is not supported")

        if self.used == IncludeUsage.PUBLIC_AND_PRIVATE:
            return

        if usage == IncludeUsage.PUBLIC_AND_PRIVATE:
            self.used = IncludeUsage.PUBLIC_AND_PRIVATE
        elif self.used == IncludeUsage.NONE:
            self.used = usage
        elif (self.used == IncludeUsage.PUBLIC and usage == IncludeUsage.PRIVATE) or (
            self.used == IncludeUsage.PRIVATE and usage == IncludeUsage.PUBLIC
        ):
            self.used = IncludeUsage.PUBLIC_AND_PRIVATE


@dataclass
class AvailableDependency:
    """A dependency and the header files it provides"""

    name: str
    hdrs: List[AvailableInclude]


class AvailableDependencies:
    """All sources for headers the target under inspection can include"""

    def __init__(
        self, own_hdrs: List[AvailableInclude], public: List[AvailableDependency], private: List[AvailableDependency]
    ) -> None:
        # Header files from target under inspection
        self.own_hdrs = own_hdrs
        # Dependecies which are available to downstream dependencies of the target under inspection
        self.public = public
        # Dependecies which are NOT available to downstream dependencies of the target under inspection
        self.private = private


def _make_available_dependency(info: Dict) -> AvailableDependency:
    dep = AvailableDependency(name=info["target"], hdrs=[])
    for hdr in info["headers"]:
        dep.hdrs.append(AvailableInclude(hdr))
    return dep


def _get_available_dependencies_impl(dependencies) -> List[AvailableDependency]:
    includes = []
    for dep in dependencies:
        avail = _make_available_dependency(dep)
        includes.append(avail)
    return includes


def get_available_dependencies(allowed_includes_file: Path) -> AvailableDependencies:
    with open(allowed_includes_file, encoding="utf-8") as fin:
        loaded = json.load(fin)
        return AvailableDependencies(
            own_hdrs=_make_available_dependency(loaded["self"]).hdrs,
            public=_get_available_dependencies_impl(loaded["public_deps"]),
            private=_get_available_dependencies_impl(loaded["private_deps"]),
        )
