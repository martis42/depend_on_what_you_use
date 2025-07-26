from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from dwyu.apply_fixes.summary import Summary

log = logging.getLogger()


class BuildozerExecutor:
    """
    Central entrypoint for executing buildozer.

    There are several options influencing how buildozer should be executed. To allow setting and processing them
    centrally once we use buildozer through the indirection of this class. Furthermore, this allows us to automatically
    build up a summary of all executed commands.
    """

    def __init__(self, buildozer: str, buildozer_args: list[str], workspace: Path, dry: bool) -> None:
        self._base_cmd = self._make_base_cmd(binary=buildozer, args=buildozer_args, dry=dry)
        self._workspace = workspace
        self._dry = dry

        self._summary = Summary()

    @property
    def summary(self) -> Summary:
        return self._summary

    def execute(self, task: str, target: str) -> None:
        command = [*self._base_cmd, task, target]
        log.log(logging.INFO if self._dry else logging.DEBUG, f"Executing buildozer command: {command}")
        process = subprocess.run(command, cwd=self._workspace, check=False, capture_output=True)
        self._summary.add_command(cmd=command, buildozer_result=process.returncode)

    @staticmethod
    def _make_base_cmd(binary: str, dry: bool, args: list[str]) -> list[str]:
        command = [binary]
        if args:
            command.extend(args)
        if dry:
            command.append("-stdout")
        return command
