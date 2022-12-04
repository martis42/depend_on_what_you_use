import json
from pathlib import Path
from typing import Optional

from src.analyze_includes.parse_source import IgnoredIncludes
from src.analyze_includes.std_header import STD_HEADER

IGNORED_PATHS_KEY = "ignore_include_paths"
EXTRA_IGNORED_PATHS_KEY = "extra_ignore_include_paths"
IGNORED_PATTERNS_KEY = "ignore_include_patterns"


def get_ignored_includes(config_file: Optional[Path]) -> IgnoredIncludes:
    ignored_paths = STD_HEADER
    ignored_patterns = []
    if config_file:
        with open(config_file, encoding="utf-8") as fin:
            config_data = json.load(fin)

            if IGNORED_PATHS_KEY in config_data:
                ignored_paths = set(config_data[IGNORED_PATHS_KEY])
            if EXTRA_IGNORED_PATHS_KEY in config_data:
                ignored_paths = ignored_paths.union(config_data[EXTRA_IGNORED_PATHS_KEY])
            if IGNORED_PATTERNS_KEY in config_data:
                ignored_patterns = config_data[IGNORED_PATTERNS_KEY]

    return IgnoredIncludes(paths=list(ignored_paths), patterns=ignored_patterns)
