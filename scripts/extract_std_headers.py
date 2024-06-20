#!/usr/bin/env python3

"""
We are interested in the following headers:
C++     - https://en.cppreference.com/w/cpp/header
C       - https://en.cppreference.com/w/c/header
POSIX C - https://en.wikipedia.org/wiki/C_POSIX_library

Go to each site and copy the content into a file. This file then reads the file and prints a list we can use in the
python file containing the standard header list for DWYU to lookup.
"""

from __future__ import annotations

import re
from pathlib import Path

INPUT = Path("input.txt")


def extract_header(text: str) -> list[str]:
    headers = []
    for line in text.split("\n"):
        headers.extend(re.findall(r"<([a-z_/.]+)>", line))
    return headers


def main() -> None:
    with INPUT.open(encoding="utf-8") as fin:
        headers = extract_header(fin.read())
        print("\n".join(f'"{h}",' for h in sorted(set(headers))))  # noqa: T201


if __name__ == "__main__":
    main()
