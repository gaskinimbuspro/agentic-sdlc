#!/usr/bin/env python3
"""Pinned dependency scans; network/scanner failures are not acceptance."""

import json
import subprocess
import sys
from pathlib import Path

from backend_standard.security import reject_findings

root = Path(__file__).resolve().parents[1]
language = sys.argv[1]
directory = root / "artifacts" / language
directory.mkdir(parents=True, exist_ok=True)
report = directory / "security.json"
if language == "python":
    requirements = directory / "requirements.txt"
    with requirements.open("w") as output:
        subprocess.run(
            [
                "uv",
                "export",
                "--project",
                "reference/python",
                "--locked",
                "--no-dev",
                "--no-emit-project",
                "--format",
                "requirements-txt",
            ],
            cwd=root,
            stdout=output,
            check=True,
        )
    subprocess.run(
        [
            "uv",
            "run",
            "--no-sync",
            "pip-audit",
            "--progress-spinner",
            "off",
            "--cache-dir",
            str(root / "artifacts/cache/pip-audit"),
            "--disable-pip",
            "--no-deps",
            "--require-hashes",
            "-r",
            str(requirements),
            "--format",
            "json",
            "--output",
            str(report),
        ],
        cwd=root,
        check=True,
    )
elif language == "go":
    with report.open("w") as output:
        subprocess.run(
            ["go", "tool", "govulncheck", "-json", "./..."],
            cwd=root / "reference/go",
            stdout=output,
            check=True,
        )
elif language == "dotnet":
    with report.open("w") as output:
        subprocess.run(
            [
                "dotnet",
                "list",
                "CustomerApi.Tests/CustomerApi.Tests.csproj",
                "package",
                "--vulnerable",
                "--include-transitive",
                "--format",
                "json",
                "--no-restore",
            ],
            cwd=root / "reference/dotnet",
            stdout=output,
            check=True,
        )
else:
    raise SystemExit("Unsupported language")
if language == "go":
    # The scanner emits concatenated JSON objects, not a single JSON array.
    decoder, content, events = json.JSONDecoder(), report.read_text(), []
    while content.strip():
        value, end = decoder.raw_decode(content.lstrip())
        events.append(value)
        content = content.lstrip()[end:]
    reject_findings(events, language)
else:
    reject_findings(json.loads(report.read_text()), language)
print(
    json.dumps(
        {
            "status": "passed",
            "scanner": language,
            "report": str(report.relative_to(root)),
        }
    )
)
