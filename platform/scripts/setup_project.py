#!/usr/bin/env python3
"""Prepare Forgejo for a project's release path.

    setup_project.py OWNER NAME --tokens DIR

Creates, when missing:
- the deploy repository OWNER/NAME-deploy (private);
- release-bot (write:package, write:repository) and deploy-reader
  (read:package, read:repository), each with a fresh token named "ci";
- the teams "release" (write) and "deploy-readers" (read) in OWNER, limited to
  the deploy repository;
- protection of main in the deploy repository: no direct push except
  overlays/staging/kustomization.yaml; everything else by pull request that
  PRODUCT_OWNER approves and merges.

Tokens are written to DIR/release-bot.token and DIR/deploy-reader.token with
mode 0600 and never printed. Re-running rotates both tokens.

Environment: FORGEJO_ADMIN_PASSWORD (required), FORGEJO_URL, FORGEJO_ADMIN,
PRODUCT_OWNER (default: FORGEJO_ADMIN).
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

URL = os.environ.get(
    "FORGEJO_URL", "http://forgejo-http.forgejo.svc.cluster.local:3000"
)
ADMIN = os.environ.get("FORGEJO_ADMIN", "forge-admin")
OWNER_USER = os.environ.get("PRODUCT_OWNER", ADMIN)
BOTS = {
    "release-bot": ["write:package", "write:repository"],
    "deploy-reader": ["read:package", "read:repository"],
}
TEAMS = {
    "release": ("write", "release-bot"),
    "deploy-readers": ("read", "deploy-reader"),
}
STAGING_FILE = "overlays/staging/kustomization.yaml"

urllib.request.install_opener(
    urllib.request.build_opener(urllib.request.ProxyHandler({}))
)


def call(
    method: str, path: str, body: Any = None, sudo: str | None = None
) -> tuple[int, Any]:
    password = os.environ["FORGEJO_ADMIN_PASSWORD"]
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(f"{URL}/api/v1{path}", data=data, method=method)
    request.add_header("Content-Type", "application/json")
    basic = base64.b64encode(f"{ADMIN}:{password}".encode()).decode()
    request.add_header("Authorization", f"Basic {basic}")
    if sudo:
        request.add_header("Sudo", sudo)
    try:
        with urllib.request.urlopen(request) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        return error.code, None


def need(result: tuple[int, Any], what: str) -> Any:
    status, body = result
    if status >= 300:
        raise SystemExit(f"{what} failed with HTTP {status}")
    return body


def write_token(directory: Path, name: str, token: str) -> None:
    path = directory / f"{name}.token"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as handle:
        handle.write(token)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("owner")
    parser.add_argument("name")
    parser.add_argument("--tokens", type=Path, required=True)
    args = parser.parse_args()
    args.tokens.mkdir(parents=True, exist_ok=True)
    deploy = f"{args.name}-deploy"

    if call("GET", f"/repos/{args.owner}/{deploy}")[0] != 200:
        need(
            call(
                "POST",
                f"/orgs/{args.owner}/repos",
                {
                    "name": deploy,
                    "private": True,
                    "auto_init": True,
                    "default_branch": "main",
                },
            ),
            "create deploy repository",
        )
        print(f"created {args.owner}/{deploy}")

    for bot, scopes in BOTS.items():
        if call("GET", f"/users/{bot}")[0] != 200:
            need(
                call(
                    "POST",
                    "/admin/users",
                    {
                        "username": bot,
                        "email": f"{bot}@forge.local",
                        "password": secrets.token_urlsafe(24),
                        "must_change_password": False,
                    },
                ),
                f"create user {bot}",
            )
            print(f"created user {bot}")
        call("DELETE", f"/users/{bot}/tokens/ci", sudo=bot)
        token = need(
            call(
                "POST",
                f"/users/{bot}/tokens",
                {"name": "ci", "scopes": scopes},
                sudo=bot,
            ),
            f"token for {bot}",
        )
        write_token(args.tokens, bot, token["sha1"])

    teams = {
        t["name"]: t["id"]
        for t in need(call("GET", f"/orgs/{args.owner}/teams"), "list teams")
    }
    for team, (permission, member) in TEAMS.items():
        if team not in teams:
            units = {
                unit: permission
                for unit in ("repo.code", "repo.packages", "repo.pulls")
            }
            created = need(
                call(
                    "POST",
                    f"/orgs/{args.owner}/teams",
                    {
                        "name": team,
                        "permission": permission,
                        "includes_all_repositories": False,
                        "units_map": units,
                    },
                ),
                f"create team {team}",
            )
            teams[team] = created["id"]
        need(call("PUT", f"/teams/{teams[team]}/members/{member}"), f"add {member}")
        need(
            call("PUT", f"/teams/{teams[team]}/repos/{args.owner}/{deploy}"),
            f"add repo to {team}",
        )

    rule = {
        "rule_name": "main",
        "enable_push": False,
        "unprotected_file_patterns": STAGING_FILE,
        "required_approvals": 1,
        "enable_approvals_whitelist": True,
        "approvals_whitelist_username": [OWNER_USER],
        "enable_merge_whitelist": True,
        "merge_whitelist_usernames": [OWNER_USER],
        "dismiss_stale_approvals": True,
        "block_on_outdated_branch": True,
    }
    base = f"/repos/{args.owner}/{deploy}/branch_protections"
    if call("GET", f"{base}/main")[0] == 200:
        need(call("PATCH", f"{base}/main", rule), "update protection")
    else:
        need(call("POST", base, rule), "protect main")
    print(
        f"{args.owner}/{deploy}: direct push only to {STAGING_FILE}; "
        f"other changes approved and merged by {OWNER_USER}. Tokens in {args.tokens}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
