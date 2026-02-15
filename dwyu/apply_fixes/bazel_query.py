from pathlib import Path
from subprocess import CompletedProcess

from dwyu.apply_fixes.utils import execute_and_capture


class BazelQuery:
    def __init__(self, workspace: Path, use_cquery: bool, query_args: list[str], startup_args: list[str]) -> None:
        self._workspace = workspace
        self._use_cquery = use_cquery
        self._query_args = query_args
        self._startup_args = startup_args

    def execute(self, query: str, args: list[str]) -> CompletedProcess:
        cmd = [
            "bazel",
            *self._startup_args,
            "cquery" if self._use_cquery else "query",
            *self._query_args,
            *args,
            query,
        ]
        return execute_and_capture(cmd=cmd, cwd=self._workspace)

    @property
    def uses_cquery(self) -> bool:
        return self._use_cquery
