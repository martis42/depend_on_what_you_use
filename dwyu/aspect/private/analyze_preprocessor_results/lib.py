from __future__ import annotations

import json
from pathlib import Path

from dwyu.aspect.private.analyze_includes.parse_source import IgnoredIncludes, Include, filter_includes


def get_relevant_includes(preprocessed_files: list[Path] | None, ignored_includes: IgnoredIncludes) -> list[Include]:
    all_includes = []
    if preprocessed_files:
        for file in preprocessed_files:
            pp_data = json.loads(file.read_text())
            for entry in pp_data:
                includes = [
                    Include(file=Path(entry["file"]), include=include.lstrip('"<').rstrip('">'))
                    for include in entry["includes"]
                ]
                all_includes.extend(includes)
    return filter_includes(includes=all_includes, ignored_includes=ignored_includes)
