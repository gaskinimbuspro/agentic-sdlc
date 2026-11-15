#!/usr/bin/env python3
"""Fail on known credential shapes without printing matched values."""

import json
import subprocess
import sys
from pathlib import Path

from backend_standard.secrets import findings

root = Path(__file__).resolve().parents[1]
names = subprocess.check_output(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
    cwd=root,
    text=True,
).splitlines()
results = []
for name in names:
    path = root / name
    try:
        content = path.read_text()
    except (UnicodeDecodeError, IsADirectoryError):
        continue
    for kind in findings(content):
        results.append({"path": name, "kind": kind})
print(json.dumps({"known_pattern_findings": results}, indent=2))
sys.exit(int(bool(results)))
