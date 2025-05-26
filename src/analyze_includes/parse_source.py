from __future__ import annotations

import re
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from pcpp.preprocessor import Action, OutputDirective, Preprocessor  # type: ignore[import-not-found]


class SimpleParsingPreprocessor(Preprocessor):
    """
    This preprocessor configuration is used to prune commented code and to resolve preprocessor statements. The main
    points for us is resolving branching statements (e.g. '#ifdef') to analyze the correct code parts.
    """

    def on_include_not_found(self, is_malformed: bool, is_system_include: bool, curdir: str, includepath: str) -> None:  # noqa: ARG002
        """
        We ignore missing include statements.

        We have many tests regarding aggregating and processing include paths which are defined through Bazel in the
        core DWYU logic for analyzing the include statements. Thus, we are confident all relevant include paths are
        provided to the preprocessor.
        We expect to fail finding system headers, as the standard library headers (aka the C++ Bazel toolchain) are
        ignored by DWYU.
        If a non toolchain header is missing we assume this is due to the header missing completely in the dependencies.
        In other words the code does not even compile and thus is violating our assumptions of use, see the README.md.
        """
        raise OutputDirective(Action.IgnoreAndPassThrough)


def make_pre_processor() -> SimpleParsingPreprocessor:
    """
    We can't overwrite member values from the base class in the ctor of our derived class and thus set them after
    construction.
    """
    processor = SimpleParsingPreprocessor()
    processor.passthru_includes = re.compile(".*")
    return processor


@dataclass
class Include:
    """Single include statement in a specific file"""

    file: Path
    include: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Include):
            return NotImplemented
        return self.file == other.file and self.include == other.include

    def __hash__(self) -> int:
        return hash(str(self.file) + self.include)

    def __repr__(self) -> str:
        return f"Include(file='{self.file}', include='{self.include}')"

    def __str__(self) -> str:
        return f"File='{self.file}', include='{self.include}'"


@dataclass
class IgnoredIncludes:
    """
    We ignore some include statements during analysis. For example header from the standard library, but also paths
    or headers chosen by the user.
    """

    paths: list[str]
    patterns: list[str]

    def is_ignored(self, include: str) -> bool:
        is_ignored_path = include in self.paths
        is_ignored_pattern = any(re.match(pattern, include) for pattern in self.patterns)
        return is_ignored_path or is_ignored_pattern


def fast_includes_extraction(file: Path) -> list[Include]:  # noqa: C901
    """
    Parse a C/C++ file and extract include statements which are not commented.

    Using this is not recommended as it has many limitations. However, pcpp is quite slow, so this can be a fallback
    for users knwoing the known limitations do not apply to them or are acceptable.

    Constraints on include statements which are used to simplify the logic:
    - Only a single include statement can exist per line. If multiple include statement exist, the compiler ignores all
      after the first one.
    - Only whitespace and commented code shall exist between the line start and the include statement.
    - One can concatenate multiple comment block openings "/*", but one cannot concatenate comment block ends "*/".
      An appearing comment block end closes all existing comment block openings.

    Known limitations:
    - Defines are inored. Thus, a superset of all mentioned headers is analyzed, even if normally a define would make
      sure only a subset of headers is used for compilation.
    - Include statements which are added through a macro are not detected.
    - Include paths utilizing '../' are not resolved.
    """
    includes = []
    inside_comment_block = False
    with file.open(encoding="utf-8") as fin:
        for raw_line in fin:
            line = raw_line.strip()
            line_without_comments = ""
            i = 0
            while i < len(line) - 1:
                curr = line[i : i + 2]
                if not inside_comment_block and curr == "//":
                    i = len(line)
                    break
                if not inside_comment_block and curr == "/*":
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
                include = re.findall(r'^\s*#include\s*["<](.+)[">]', line_without_comments)
                if not include:
                    raise RuntimeError(f"Did not find any include path in file '{file}' in line '{line}'")
                if len(include) > 1:
                    raise RuntimeError(f"Found unexpectedly multiple include paths in file '{file}' in line '{line}'")
                includes.append(Include(file=file, include=include[0]))
    return includes


def extract_includes(file: Path, defines: list[str], include_paths: list[str]) -> list[Include]:
    """
    Parse a C/C++ file and extract include statements which are neither commented nor disabled through pre processor
    branching (e.g. #ifdef).

    The preprocessor removes all comments and inactive code branches. This allows us then to find all include statements
    with a simple regex.
    """
    with file.open(encoding="utf-8") as fin:
        pre_processor = make_pre_processor()
        for define in defines:
            pre_processor.define(define)
        for path in include_paths:
            pre_processor.add_path(path)

        pre_processor.parse(fin.read())
        output_sink = StringIO()
        pre_processor.write(output_sink)

        included_paths = []
        for include in re.findall(r"^\s*#include\s*(.+)", output_sink.getvalue(), re.MULTILINE):
            if include.startswith(('"', "<")) and include.endswith(('"', ">")):
                included_paths.append(include)
            elif include in pre_processor.macros:
                # Either a malformed include statement or an include path defined through a pre processor token.
                # We ignore malformed include paths as they violate our assumptions of use.
                # 'macros' is a {str: 'Macro'} dictionary based on pcpp.parser.Macro.
                # The value is a list of 'LexToken' classes from 'ply.lex.LexToken'.
                # In all our tests with include statements the list had always just one element.
                included_paths.append(pre_processor.macros[include].value[0].value)

        return [Include(file=file, include=include.lstrip('"<').rstrip('">')) for include in included_paths]


def filter_includes(includes: list[Include], ignored_includes: IgnoredIncludes) -> list[Include]:
    """
    - deduplicate list entries
    - throw away uninteresting includes (e.g. from standard library or ignored includes provided by the user)
    """
    unique_includes = set(includes)
    return [include for include in unique_includes if not ignored_includes.is_ignored(include.include)]


def get_relevant_includes_from_files(
    files: list[str] | None,
    ignored_includes: IgnoredIncludes,
    defines: list[str],
    include_paths: list[str],
    no_preprocessor: bool,
) -> list[Include]:
    all_includes = []
    if files:
        for file in files:
            if no_preprocessor:
                includes = fast_includes_extraction(file=Path(file))
            else:
                includes = extract_includes(file=Path(file), defines=defines, include_paths=include_paths)
            all_includes.extend(includes)
    return filter_includes(includes=all_includes, ignored_includes=ignored_includes)
