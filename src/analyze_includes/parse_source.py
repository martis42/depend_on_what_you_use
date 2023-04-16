import re
from io import StringIO
from pathlib import Path
from typing import List, Union

from pcpp import Preprocessor


class SimpleParsingPreprocessor(Preprocessor):
    """
    This preprocessor configuration is used to prune commented code and to resolve preprocessor statements for defines
    which are injected through Bazel. We do not resolve include statements. Meaning each file is analyzed only for
    itself.
    """

    def on_file_open(self, _, __):
        """
        Raising here prevents include statements being resolved
        """
        raise OSError("Do not open file")

    def on_error(self, _, __, ___):
        """
        Since unresolved include statements cause errors we silence error reporting
        """
        pass


class Include:
    """Single include statement in a specific file"""

    def __init__(self, file: Path, include: str) -> None:
        self.file = file
        self.include = include

    def __eq__(self, other: object) -> bool:
        return self.file == other.file and self.include == other.include

    def __hash__(self) -> int:
        return hash(str(self.file) + self.include)

    def __repr__(self) -> str:
        return f"Include(file='{self.file}', include='{self.include}')"

    def __str__(self) -> str:
        return f"File='{self.file}', include='{self.include}'"


class IgnoredIncludes:
    """
    We ignore some include statements during analysis. For example header from the standard library, but also paths
    or headers chosen by the user.
    """

    def __init__(self, paths: List[str], patterns: List[str]) -> None:
        self.paths = paths
        self.patterns = patterns

    def is_ignored(self, include: str) -> bool:
        is_ignored_path = include in self.paths
        is_ignored_pattern = any(re.match(pattern, include) for pattern in self.patterns)
        return is_ignored_path or is_ignored_pattern


def get_includes_from_file(file: Path, defines: List[str]) -> List[Include]:
    """
    Parse a C/C++ file and extract include statements which are neither commented nor disabled through a define.
    """
    with open(file, encoding="utf-8") as fin:
        pre_processor = SimpleParsingPreprocessor()
        for define in defines:
            pre_processor.define(define)
        pre_processor.parse(fin.read())

        output_sink = StringIO()
        pre_processor.write(output_sink)

        return [
            Include(file=file, include=include)
            for include in re.findall(r'^\s*#include\s*["<](.+)[">]', output_sink.getvalue(), re.MULTILINE)
        ]


def filter_includes(includes: List[Include], ignored_includes: IgnoredIncludes) -> List[Include]:
    """
    - deduplicate list entries
    - throw away uninteresting includes (e.g. from standard library or ignored includes provided by the user)
    """
    unique_includes = set(includes)
    return [include for include in unique_includes if not ignored_includes.is_ignored(include.include)]


def get_relevant_includes_from_files(
    files: Union[List[str], None], ignored_includes: IgnoredIncludes, defines: List[str]
) -> List[Include]:
    all_includes = []
    if files:
        for file in files:
            includes = get_includes_from_file(file=Path(file), defines=defines)
            all_includes.extend(includes)
    return filter_includes(includes=all_includes, ignored_includes=ignored_includes)
