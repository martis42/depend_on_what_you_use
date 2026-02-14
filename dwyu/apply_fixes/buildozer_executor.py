from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from platform import system

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
        # command = [*self._base_cmd, task, self._make_windows_cmd2(target)]
        # command = [*self._base_cmd, task, target]
        # if system() == "Windows":
        #    command = self._make_windows_cmd(command)
        log.log(logging.INFO if self._dry else logging.DEBUG, f"Executing buildozer command: {command}")
        process = subprocess.run(command, cwd=self._workspace, check=False, capture_output=True)
        self._summary.add_command(cmd=command, buildozer_result=process.returncode)

    def adapt_to_platform(self, targets: str | list[str]) -> str | list[str]:
        """
        Buildozer interprets the target label after the workspace root '//' as a path. Thus, on Windows we have to use
        backslashes instead of forward slashes.
        """
        if isinstance(targets, str):
            return self._adapt_to_platform_impl(targets)
        return [self._adapt_to_platform_impl(t) for t in targets]

    @staticmethod
    def _adapt_to_platform_impl(target: str) -> str:
        if system() == "Windows":
            return target.replace("//", "::PLACEHOLDER::").replace("/", "\\").replace("::PLACEHOLDER::", "//")
        return target

    @staticmethod
    def _make_base_cmd(binary: str, dry: bool, args: list[str]) -> list[str]:
        command = [binary]
        if args:
            command.extend(args)
        if dry:
            command.append("-stdout")
        return command

    # @staticmethod
    # def _make_windows_cmd(mcd: list[str]) -> list[str]:
    #     """
    #     TODO explain why this is needed and what it does
    #     """
    #     return [c.replace("//", "::PLACEHOLDER::").replace("/", "\\").replace("::PLACEHOLDER::", "//") for c in mcd]

    # @staticmethod
    # def _make_windows_cmd2(cmd: str) -> str:
    #     """
    #     TODO explain why this is needed and what it does
    #     """
    #     if system() == "Windows":
    #         return cmd.replace("//", "::PLACEHOLDER::").replace("/", "\\").replace("::PLACEHOLDER::", "//")
    #     return cmd
