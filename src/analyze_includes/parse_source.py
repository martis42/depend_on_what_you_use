import re
from pathlib import Path
from typing import List, Union


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


def get_includes_from_file(file: Path) -> List[Include]:
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
    - Defines are inored. Thus, a superset of all mentioned headers is analyzed, even if normally a define would make
      sure only a subset of headers is used for compilation.
    - Include paths utilizing '../' are not resolved.
    """
    includes, inside_comment_block = [], False
    with open(file, encoding="utf-8") as fin:
        for line in fin:
            line = line.rstrip()
            line_without_comments = ""
            i = 0
            while i < len(line) - 1:
                curr = line[i : i + 2]
                if not inside_comment_block and curr == "//":
                    i = len(line)
                    break
                elif not inside_comment_block and curr == "/*":
                    inside_comment_block = True
                    i += 1
                elif inside_comment_block and curr == "*/":
                    inside_comment_block = False
                    i += 1
                elif not inside_comment_block:
                    line_without_comments += line[i]
                i += 1
            if line and not inside_comment_block and i < len(line):
                line_without_comments += line[-1]

            if (
                not inside_comment_block
                and line_without_comments
                and line_without_comments.lstrip().startswith("#include")
            ):
                include = re.findall(r'#include\s*["<](.+)[">]', line_without_comments)
                if not include:
                    raise Exception(f"Did not find any include path in file '{file}' in line '{line}'")
                if len(include) > 1:
                    raise Exception(f"Found unexpectedly multiple include paths in file '{file}' in line '{line}'")
                includes.append(Include(file=file, include=include[0]))
    return includes


def filter_includes(includes: List[Include], ignored_includes: IgnoredIncludes) -> List[Include]:
    """
    - deduplicate list entries
    - throw away uninteresting includes (e.g. from standard library or ignored includes provided by the user)
    """
    unique_includes = set(includes)
    return [include for include in unique_includes if not ignored_includes.is_ignored(include.include)]


def get_relevant_includes_from_files(files: Union[List[str], None], ignored_includes: IgnoredIncludes) -> List[Include]:
    all_includes = []
    if files:
        for file in files:
            includes = get_includes_from_file(Path(file))
            all_includes.extend(includes)
    return filter_includes(includes=all_includes, ignored_includes=ignored_includes)
