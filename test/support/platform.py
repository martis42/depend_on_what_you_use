from __future__ import annotations

from pathlib import Path, PosixPath


def path_to_starlark_format(path: Path) -> str:
    """
    We can't use the path directly on Windows as we need escaped backslashes on Windows
    """
    return str(path) if isinstance(path, PosixPath) else str(path).replace("\\", "\\\\")
