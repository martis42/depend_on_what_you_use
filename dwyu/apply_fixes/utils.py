from __future__ import annotations

import logging
import shlex
import subprocess
from pathlib import Path

log = logging.getLogger()


def args_string_to_list(args: str | None) -> list[str]:
    return shlex.split(args) if args else []


def execute_and_capture(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    log.debug(f"Executing command: {shlex.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
