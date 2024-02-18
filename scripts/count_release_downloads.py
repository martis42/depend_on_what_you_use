#!/usr/bin/env python3

"""
From version 0.1.0 on we package a dedicated DWYU archive as part of each release for which we can get download
statistics.
"""

# No benefit for using logging here
# ruff: noqa: T201

import json
import subprocess

token = input("Please provide an access token with permissions 'contents:read': ")

cmd = [
    "curl",
    "-L",
    "-H",
    "Accept: application/vnd.github+json",
    "-H",
    f"Authorization: Bearer {token}",
    "-H",
    "X-GitHub-Api-Version: 2022-11-28",
    "https://api.github.com/repos/martis42/depend_on_what_you_use/releases",
]
process = subprocess.run(cmd, check=True, capture_output=True, text=True)
reply = json.loads(process.stdout.strip())

for release in reply:
    print(f"Release '{release['name']}'")
    if "assets" not in release:
        print("  No assets")
    for asset in release["assets"]:
        print(f"  {asset['name']}: {asset['download_count']}")
