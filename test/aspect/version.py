from dataclasses import dataclass


@dataclass
class TestedVersions:
    bazel: str
    python: str
    is_default: bool = False


@dataclass
class CompatibleVersions:
    minimum: str = ""
    before: str = ""

    def is_compatible_to(self, version: str) -> bool:
        if version == "rolling":
            # Ignore 'minimum' as it cannot be incompatible to 'rolling'
            # 'rolling' cannot be compatible to any 'before'
            return self.before == ""

        if self.minimum == "rolling":
            return False
        if self.before == "rolling":
            return True

        comply_with_min_version = version >= self.minimum if self.minimum else True
        comply_with_max_version = version < self.before if self.before else True
        return comply_with_min_version and comply_with_max_version
