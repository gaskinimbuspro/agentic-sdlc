"""Check tracked/source Markdown paths/anchors, templates, and stable rule IDs."""

import collections
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def slug(value):
    value = re.sub(r"<[^>]*>", "", value).replace("`", "").replace("*", "").lower()
    return "".join(
        c for c in value if c in " -_" or unicodedata.category(c)[0] in "LN"
    ).replace(" ", "-")


def anchors(path):
    content = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
    seen, result = collections.Counter(), set()
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*$", content, re.M):
        name = slug(heading)
        result.add(name + (f"-{seen[name]}" if seen[name] else ""))
        seen[name] += 1
    return result


def main():
    names = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
    ).splitlines()
    failures, links = [], 0
    for name in names:
        path = ROOT / name
        if path.suffix == ".json":
            try:
                json.loads(path.read_text())
            except ValueError:
                failures.append(f"Invalid JSON: {name}")
        if path.suffix != ".md":
            continue
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("mailto:"):
                continue
            links += 1
            relative, _, fragment = target.partition("#")
            destination = (path.parent / relative).resolve() if relative else path
            if not destination.exists():
                failures.append(f"{name}: missing {target}")
            elif (
                fragment
                and destination.suffix == ".md"
                and fragment not in anchors(destination)
            ):
                failures.append(f"{name}: missing anchor {target}")
    expected = {
        "common.md": ("B", 18),
        "testing.md": ("T", 10),
        "profiles/python.md": ("PY", 7),
        "profiles/dotnet.md": ("NET", 7),
        "profiles/go.md": ("GO", 8),
        "definition-of-done.md": ("D", 10),
        "test-case-matrix.md": ("TC", 14),
    }
    for filename, (prefix, count) in expected.items():
        found = re.findall(
            rf"^\| ({prefix}\d{{2}}) \|",
            (ROOT / "standards/backend" / filename).read_text(),
            re.M,
        )
        if found != [f"{prefix}{i:02}" for i in range(1, count + 1)]:
            failures.append(f"Rule IDs changed: {filename}")
    rows = re.findall(
        r"^\| ((?:B|T)\d{2}):",
        (ROOT / "standards/backend/verification-matrix.md").read_text(),
        re.M,
    )
    if rows != [f"B{i:02}" for i in range(1, 19)] + [f"T{i:02}" for i in range(1, 11)]:
        failures.append("Incomplete matrix coverage")
    print(
        json.dumps(
            {"local_links": links, "matrix_rules": len(rows), "errors": failures},
            indent=2,
        )
    )
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
