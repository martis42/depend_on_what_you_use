from __future__ import annotations

import re
from dataclasses import dataclass
from io import StringIO
from pathlib import Path

from pcpp.preprocessor import Action, OutputDirective, Preprocessor


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


def get_includes_from_file(file: Path, defines: list[str], include_paths: list[str]) -> list[Include]:
    """
    Parse a C/C++ file and extract include statements which are neither commented nor disabled through pre processor
    branching (e.g. #ifdef).

    The preprocessor removes all comments and inactive code branches. This allows us then to find all include statements
    with a simple regex.
    """
    with open(file, encoding="utf-8") as fin:
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
    files: list[str] | None, ignored_includes: IgnoredIncludes, defines: list[str], include_paths: list[str]
) -> list[Include]:
    all_includes = []
    if files:
        for file in files:
            includes = get_includes_from_file(file=Path(file), defines=defines, include_paths=include_paths)
            all_includes.extend(includes)
    return filter_includes(includes=all_includes, ignored_includes=ignored_includes)
