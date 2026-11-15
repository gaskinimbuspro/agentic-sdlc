#!/usr/bin/env python3
"""Run the common acceptance suite against a packaged backend and disposable PG."""

import argparse
import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
POSTGRES_IMAGE = "postgres:18.7-bookworm@sha256:ece55f7868da684e400f82f1030a050718adbdd65c23aa500c486f6e2950dc0f"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("language", choices=["python", "go", "dotnet"])
    parser.add_argument("--external-database", action="store_true")
    parser.add_argument("--browser", action="store_true")
    args = parser.parse_args()
    if args.browser and args.language != "python":
        parser.error("The browser pilot uses the packaged Python reference")
    artifacts = ROOT / "artifacts" / ("frontend" if args.browser else args.language)
    artifacts.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    container = None
    if not args.external_database:
        env.update(
            DB_HOST="127.0.0.1",
            DB_NAME="backend_reference",
            DB_USER="postgres",
            DB_PASSWORD=secrets.token_urlsafe(32),
        )
        # Passing environment names keeps the generated password out of argv/logs.
        docker_env = dict(
            env, POSTGRES_PASSWORD=env["DB_PASSWORD"], POSTGRES_DB=env["DB_NAME"]
        )
        container = subprocess.check_output(
            [
                "docker",
                "run",
                "--rm",
                "-d",
                "-p",
                "127.0.0.1::5432",
                "--env",
                "POSTGRES_PASSWORD",
                "--env",
                "POSTGRES_DB",
                POSTGRES_IMAGE,
            ],
            env=docker_env,
            text=True,
        ).strip()
        binding = json.loads(
            subprocess.check_output(["docker", "inspect", container], text=True)
        )[0]
        env["DB_PORT"] = binding["NetworkSettings"]["Ports"]["5432/tcp"][0]["HostPort"]
    try:
        deadline = time.monotonic() + 45
        while True:
            try:
                with psycopg.connect(
                    host=env["DB_HOST"],
                    port=env["DB_PORT"],
                    dbname=env["DB_NAME"],
                    user=env["DB_USER"],
                    password=env["DB_PASSWORD"],
                    connect_timeout=1,
                ):
                    break
            except psycopg.OperationalError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("PostgreSQL did not become ready") from None
                time.sleep(0.2)
        commands = {
            "python": [
                str(ROOT / "reference/python/.venv/bin/python"),
                "-m",
                "uvicorn",
                "customer_api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
            ],
            "go": [str(ROOT / "artifacts/go/customer-api")],
            "dotnet": [
                "dotnet",
                str(ROOT / "artifacts/dotnet/publish/CustomerApi.dll"),
            ],
        }
        # Python's port comes from the environment via a tiny launcher module.
        if args.language == "python":
            commands["python"] = [
                str(ROOT / "reference/python/.venv/bin/python"),
                "-m",
                "customer_api.serve",
            ]
        env["REFERENCE_COMMAND"] = json.dumps(commands[args.language])
        frontend = "tests/acceptance/test_frontend.py"
        suite = (
            [frontend] if args.browser else ["tests/acceptance", "--ignore=" + frontend]
        )
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                *suite,
                "--junitxml=" + str(artifacts / "acceptance.xml"),
            ],
            cwd=ROOT,
            env=env,
            check=False,
        ).returncode
    finally:
        if container:
            subprocess.run(
                ["docker", "rm", "-f", container],
                check=False,
                stdout=subprocess.DEVNULL,
            )


if __name__ == "__main__":
    sys.exit(main())
