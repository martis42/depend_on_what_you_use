from __future__ import annotations

from pathlib import PosixPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def path_to_starlark_format(path: Path) -> str:
    """
    We can't use the path directly on Windows as we need escaped backslashes on Windows
    """
    return str(path) if isinstance(path, PosixPath) else str(path).replace("\\", "\\\\")
