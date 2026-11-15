"""CLI with explicit failure status; never turns blocked checks into green."""

import argparse
import json
import sys
from pathlib import Path

from backend_standard.gates import Rejected, document, profile_ready, verify_evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    ready = sub.add_parser("profile")
    ready.add_argument("path", type=Path)
    ready.add_argument("--root", type=Path, default=Path.cwd())
    evidence = sub.add_parser("evidence")
    evidence.add_argument("path", type=Path)
    evidence.add_argument("--policy", type=Path, required=True)
    evidence.add_argument("--reports", type=Path, required=True)
    evidence.add_argument("--candidate", required=True)
    evidence.add_argument("--base", required=True)
    args = parser.parse_args()
    try:
        if args.command == "profile":
            profile_ready(document(args.path), args.root)
        else:
            verify_evidence(
                document(args.policy),
                document(args.path),
                args.reports,
                args.candidate,
                args.base,
            )
    except (Rejected, ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {"status": "passed", "scope": "input validation, not external attestation"}
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
