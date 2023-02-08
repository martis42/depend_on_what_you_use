import re
from pathlib import Path
from typing import List, Union

from clang.cindex import CursorKind, TranslationUnit


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


def get_includes_from_file(file: Path, compile_flags: Union[List[str], None] = None) -> List[Include]:
    """
    Parse a C/C++ file and extract include statements which are neither commented nor disabled through a define.

    Constraints on include statements which are used to simplify the logic:
    - Only a single include statement can exist per line. If multiple include statement exist, the compiler ignores all
      after the first one.
    - Only whitespace and commented code shall exist between the line start and the include statement.
    - One can concatenate multiple comment block openings "/*", but one cannot concatenate comment block ends "*/".
      An appearing comment block end closes all existing comment block openings.

    Known limitations:
    - Include statements which are added through a macro are not detected.
    - Include paths utilizing '../' are not resolved.
    """

    # NOTE(storypku): Why parsing w/ the PARSE_DETAILED_PROCESSING_RECORD option?
    # 1. Indicates that the parser should construct a detailed preprocessing record,
    #    including all macro definitions and instantiations
    # 2. Required to retrieve `CursorKind.INCLUSION_DIRECTIVE`
    includes = []

    parse_options = TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD | TranslationUnit.PARSE_SKIP_FUNCTION_BODIES
    translation_unit = TranslationUnit.from_source(file, compile_flags, None, parse_options, None)
    for child in translation_unit.cursor.get_children():
        if child.kind == CursorKind.INCLUSION_DIRECTIVE and child.location.file.name == str(file):
            includes.append(Include(file=file, include=child.spelling))

    return includes


def filter_includes(includes: List[Include], ignored_includes: IgnoredIncludes) -> List[Include]:
    """
    - deduplicate list entries
    - throw away uninteresting includes (e.g. from standard library or ignored includes provided by the user)
    """
    unique_includes = set(includes)
    return [include for include in unique_includes if not ignored_includes.is_ignored(include.include)]


def get_relevant_includes_from_files(
    files: Union[List[str], None],
    ignored_includes: IgnoredIncludes,
    compile_flags: Union[List[str], None] = None,
) -> List[Include]:
    all_includes = []
    if files:
        for file in files:
            includes = get_includes_from_file(Path(file), compile_flags)
            all_includes.extend(includes)
    return filter_includes(includes=all_includes, ignored_includes=ignored_includes)
