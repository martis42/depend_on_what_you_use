import json
from pathlib import Path
from typing import List, Tuple


def load_config(config: Path) -> Tuple[List[str], List[str]]:
    with open(config, encoding="utf-8") as fin:
        loaded = json.load(fin)
        ignored_includes = loaded["ignore_include_paths"]
        extra_ignored_includes = loaded["extra_ignore_include_paths"]
        ignored_patterns = loaded["ignore_include_patterns"]
        return ignored_includes, extra_ignored_includes, ignored_patterns
