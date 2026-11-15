#!/usr/bin/env python3
"""Run named checks, preserving failures, counts and a non-authoritative index."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from backend_standard.gates import Rejected, test_counts

ROOT = Path(__file__).resolve().parents[1]


def checks(language):
    uv = ["uv", "run", "--no-sync"]
    if language == "tools":
        return [
            (
                "format",
                uv
                + [
                    "ruff",
                    "format",
                    "--check",
                    "src",
                    "tests",
                    "scripts/backend_verify.py",
                    "scripts/reference_acceptance.py",
                    "scripts/check_standard.py",
                ],
                ROOT,
                None,
            ),
            (
                "lint",
                uv
                + [
                    "ruff",
                    "check",
                    "src",
                    "tests",
                    "scripts/backend_verify.py",
                    "scripts/reference_acceptance.py",
                    "scripts/check_standard.py",
                ],
                ROOT,
                None,
            ),
            ("types", uv + ["mypy", "--strict", "src"], ROOT, None),
            ("documents", [sys.executable, "scripts/check_standard.py"], ROOT, None),
            (
                "unit",
                uv + ["pytest", "tests/unit", "--junitxml=artifacts/tools/unit.xml"],
                ROOT,
                "junit",
            ),
        ]
    if language == "python":
        project = ROOT / "reference/python"
        return [
            ("format", uv + ["ruff", "format", "--check", "."], project, None),
            ("lint", uv + ["ruff", "check", "."], project, None),
            ("types", uv + ["mypy", "--strict", "src"], project, None),
            (
                "unit",
                uv + ["pytest", "tests", "--junitxml=../../artifacts/python/unit.xml"],
                project,
                "junit",
            ),
            (
                "package",
                ["uv", "build", "--out-dir", "../../artifacts/python/dist"],
                project,
                None,
            ),
            (
                "install-artifact",
                [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    ".venv/bin/python",
                    "--no-deps",
                    "../../artifacts/python/dist/customer_api_reference-0.1.0-py3-none-any.whl",
                ],
                project,
                None,
            ),
            (
                "acceptance",
                [sys.executable, "scripts/reference_acceptance.py", "python"],
                ROOT,
                "junit",
            ),
        ]
    if language == "go":
        project = ROOT / "reference/go"
        return [
            (
                "format",
                [sys.executable, str(ROOT / "scripts/go_format.py")],
                project,
                None,
            ),
            ("tidy", ["go", "mod", "tidy", "-diff"], project, None),
            ("dependencies", ["go", "mod", "verify"], project, None),
            ("static", ["go", "vet", "-mod=readonly", "./..."], project, None),
            (
                "unit",
                ["go", "test", "-mod=readonly", "-count=1", "-race", "-json", "./..."],
                project,
                "go-json",
            ),
            (
                "package",
                [
                    "go",
                    "build",
                    "-mod=readonly",
                    "-trimpath",
                    "-buildvcs=false",
                    "-o",
                    "../../artifacts/go/customer-api",
                    ".",
                ],
                project,
                None,
            ),
            (
                "acceptance",
                [sys.executable, "scripts/reference_acceptance.py", "go"],
                ROOT,
                "junit",
            ),
        ]
    project = ROOT / "reference/dotnet"
    return [
        (
            "restore",
            [
                "dotnet",
                "restore",
                "CustomerApi.Tests/CustomerApi.Tests.csproj",
                "--locked-mode",
                "-warnaserror",
            ],
            project,
            None,
        ),
        (
            "format",
            [
                "dotnet",
                "format",
                "CustomerApi.Tests/CustomerApi.Tests.csproj",
                "--verify-no-changes",
                "--no-restore",
            ],
            project,
            None,
        ),
        (
            "build",
            [
                "dotnet",
                "build",
                "CustomerApi.Tests/CustomerApi.Tests.csproj",
                "-c",
                "Release",
                "--no-restore",
                "-warnaserror",
            ],
            project,
            None,
        ),
        (
            "unit",
            [
                "dotnet",
                "test",
                "CustomerApi.Tests/CustomerApi.Tests.csproj",
                "-c",
                "Release",
                "--no-build",
                "--no-restore",
                "--logger",
                "trx;LogFileName=unit.trx",
                "--results-directory",
                str(ROOT / "artifacts/dotnet"),
            ],
            project,
            "trx",
        ),
        (
            "package",
            [
                "dotnet",
                "publish",
                "CustomerApi/CustomerApi.csproj",
                "-c",
                "Release",
                "--no-restore",
                "-o",
                str(ROOT / "artifacts/dotnet/publish"),
            ],
            project,
            None,
        ),
        (
            "acceptance",
            [sys.executable, "scripts/reference_acceptance.py", "dotnet"],
            ROOT,
            "junit",
        ),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("language", choices=["tools", "python", "go", "dotnet", "all"])
    args = parser.parse_args()
    os.environ.setdefault("UV_CACHE_DIR", str(ROOT / "artifacts/cache/uv"))
    os.environ.setdefault("GOCACHE", str(ROOT / "artifacts/cache/go"))
    os.environ.setdefault("GOMODCACHE", str(ROOT / "artifacts/cache/go-mod"))
    os.environ.setdefault("GOTOOLCHAIN", "local")
    languages = (
        ["tools", "python", "go", "dotnet"]
        if args.language == "all"
        else [args.language]
    )
    failed = False
    for language in languages:
        directory = ROOT / "artifacts" / language
        directory.mkdir(parents=True, exist_ok=True)
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=ROOT, text=True
            )
        )
        results = []
        for name, command, cwd, report_format in checks(language):
            started = time.monotonic()
            log = directory / (name + ".log")
            status, code, reason = "passed", 0, None
            with log.open("w") as output:
                try:
                    if shutil.which(command[0]) is None:
                        raise FileNotFoundError(command[0])
                    completed = subprocess.run(
                        command,
                        cwd=cwd,
                        stdout=output,
                        stderr=subprocess.STDOUT,
                        timeout=300,
                        check=False,
                    )
                    code = completed.returncode
                    if code != 0:
                        status, reason = "failed", "Command failed"
                except (FileNotFoundError, subprocess.TimeoutExpired) as error:
                    status, code, reason = "blocked", 1, type(error).__name__
            record = {
                "name": name,
                "command": command,
                "candidate_sha": sha,
                "dirty": dirty,
                "status": status,
                "exit_code": code,
                "duration_seconds": round(time.monotonic() - started, 3),
                "log": str(log.relative_to(ROOT)),
                "sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
            }
            if reason:
                record["reason"] = reason
            if report_format and status == "passed":
                report = directory / (
                    ("acceptance.xml" if name == "acceptance" else "unit.xml")
                    if report_format == "junit"
                    else "unit.trx"
                )
                if report_format == "go-json":
                    report = log
                try:
                    record["counts"] = test_counts(report, report_format)
                    record["report"] = str(report.relative_to(ROOT))
                    record["report_sha256"] = hashlib.sha256(
                        report.read_bytes()
                    ).hexdigest()
                except (Rejected, OSError, ValueError) as error:
                    record.update(status="failed", reason=str(error), exit_code=1)
            results.append(record)
            print(f"{language}/{name}: {record['status']}", flush=True)
            if record["status"] != "passed":
                print(log.read_text()[-5000:], flush=True)
                failed = True
                break  # Dependent checks cannot run against a missing/stale artifact.
        index = {
            "scope": "local checks only; independent review/integration acceptance required",
            "candidate_sha": sha,
            "dirty": dirty,
            "checks": results,
            "status": "passed"
            if len(results) == len(checks(language))
            and all(r["status"] == "passed" for r in results)
            else "blocked",
        }
        (directory / "results.json").write_text(json.dumps(index, indent=2) + "\n")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
