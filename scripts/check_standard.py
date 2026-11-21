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
    ui_rules = 0
    for filename, prefix, count in (
        ("common.md", "U", 16),
        ("testing.md", "UT", 10),
        ("test-case-matrix.md", "UC", 12),
        ("definition-of-done.md", "UD", 10),
    ):
        found = re.findall(
            rf"^\| ({prefix}\d{{2}}) \|",
            (ROOT / "standards/ui" / filename).read_text(),
            re.M,
        )
        ui_rules += len(found)
        if found != [f"{prefix}{i:02}" for i in range(1, count + 1)]:
            failures.append(f"UI rule IDs changed: {filename}")
    rows = re.findall(
        r"^\| ((?:B|T)\d{2}):",
        (ROOT / "standards/backend/verification-matrix.md").read_text(),
        re.M,
    )
    if rows != [f"B{i:02}" for i in range(1, 19)] + [f"T{i:02}" for i in range(1, 11)]:
        failures.append("Incomplete matrix coverage")
    operations_rules = 0
    for filename, prefix in (
        ("database.md", "DB"),
        ("platform.md", "PL"),
        ("security.md", "SEC"),
    ):
        found = re.findall(
            rf"^\| ({prefix}\d{{2}}) \|",
            (ROOT / "standards/operations" / filename).read_text(),
            re.M,
        )
        operations_rules += len(found)
        if found != [f"{prefix}{i:02}" for i in range(1, 9)]:
            failures.append(f"Operations rule IDs changed: {filename}")
    dispatch_rules = re.findall(
        r"^\| (AD\d{2}) \|",
        (ROOT / "standards/agent-delivery/README.md").read_text(),
        re.M,
    )
    if dispatch_rules != [f"AD{i:02}" for i in range(1, 9)]:
        failures.append("Agent delivery rule IDs changed")
    added_rules = 0
    for filename, prefix, count in (
        ("planning/requirements.md", "RQ", 6),
        ("planning/architecture.md", "AR", 5),
        ("agent-delivery/security.md", "AS", 8),
        ("agent-delivery/integration.md", "IN", 5),
        ("agent-delivery/measurement.md", "ME", 6),
        ("operations/reliability.md", "RL", 6),
        ("operations/privacy.md", "PV", 5),
        ("adoption/gitops.md", "GT", 6),
        ("ui/design-process.md", "UX", 14),
        ("operations/schema-design.md", "DD", 20),
        ("planning/discovery.md", "DQ", 6),
    ):
        found = re.findall(
            rf"^\| ({prefix}\d{{2}}) \|",
            (ROOT / "standards" / filename).read_text(),
            re.M,
        )
        added_rules += len(found)
        if found != [f"{prefix}{i:02}" for i in range(1, count + 1)]:
            failures.append(f"Rule IDs changed: {filename}")
    defined = collections.defaultdict(set)
    for name in names:
        if name.startswith("standards/") and name.endswith(".md"):
            for rule in re.findall(
                r"^\| ([A-Z]+\d{2}) \|", (ROOT / name).read_text(), re.M
            ):
                defined[rule].add(name)
    for rule, files in sorted(defined.items()):
        if len(files) > 1:
            failures.append(f"Rule ID {rule} defined in: {', '.join(sorted(files))}")
    print(
        json.dumps(
            {
                "local_links": links,
                "matrix_rules": len(rows),
                "ui_rules": ui_rules,
                "operations_rules": operations_rules,
                "agent_delivery_rules": len(dispatch_rules),
                "planning_security_reliability_rules": added_rules,
                "unique_rule_ids": len(defined),
                "errors": failures,
            },
            indent=2,
        )
    )
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
