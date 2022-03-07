#!/usr/bin/env python3

"""
Given a file containing the text of https://en.cppreference.com/w/cpp/header create a list of std headers
"""

import re

INPUT_FILE = "content_of_cppreference.txt"

with open(INPUT_FILE, mode="r", encoding="utf-8") as fin:
    for line in fin.readlines():
        include = re.findall("^<(.+)>$", line)
        if len(include) == 1:
            print(f'"{include[0]}",')
