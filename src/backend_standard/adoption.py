"""Verify candidate-bound evidence for selected production adoption profiles."""

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

from backend_standard.gates import Rejected, confined, require, text

MAX_RECORD_BYTES = 4_000_000


def _case_ids(prefix: str, count: int) -> set[str]:
    return {f"{prefix}{number:02}" for number in range(1, count + 1)}


PROFILE_CASES = {
    "identity": _case_ids("ID", 6),
    "gitops": _case_ids("GT", 6),
    "github": _case_ids("GH", 6),
    "accessibility": _case_ids("AX", 6),
    "remote": _case_ids("O", 12) | _case_ids("RP", 6),
}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj = dict(pairs)
    require(len(obj) == len(pairs), "Duplicate JSON member in adoption record")
    return obj


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise Rejected(f"{label}: expected an object")
    return value


def read_adoption_record(path: Path, digest: str | None = None) -> dict[str, Any]:
    with path.open("rb") as handle:
        raw = handle.read(MAX_RECORD_BYTES + 1)
    require(len(raw) <= MAX_RECORD_BYTES, "Adoption record exceeds size limit")
    if digest is not None:
        actual = "sha256:" + hashlib.sha256(raw).hexdigest()
        require(digest == actual, "Adoption report digest mismatch")
    try:
        record = json.loads(raw, object_pairs_hook=_unique_object)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise Rejected("Invalid adoption JSON record") from error
    return _object(record, "Adoption record")


def _timestamp(value: object) -> int:
    if type(value) is not int or value <= 0:
        raise Rejected("Soak timestamps must be positive integer Unix seconds")
    return value


def _verify_soak(value: object, approved: object) -> None:
    window = _object(approved, "Approved remote window")
    not_before = _timestamp(window.get("not_before"))
    not_after = _timestamp(window.get("not_after"))
    soak = _object(value, "Soak")
    start = _timestamp(soak.get("started_at"))
    end = _timestamp(soak.get("ended_at"))
    require(
        not_before <= start < end <= not_after,
        "Soak falls outside the approved run window",
    )
    require(end <= time.time(), "Soak contains future observations")
    require(end - start >= 86_400, "Soak must span at least 24 hours")
    samples = soak.get("samples")
    if not isinstance(samples, list) or not samples:
        raise Rejected("Soak samples required")

    previous = None
    previous_activity = None
    period_start = start
    durations = {"idle": 0, "workload": 0}
    for raw in samples:
        sample = _object(raw, "Soak sample")
        at = _timestamp(sample.get("at"))
        if previous is None:
            require(
                at == start, "Soak sample coverage must start at the window boundary"
            )
        else:
            require(
                0 < at - previous <= 300,
                "Soak samples are unordered or exceed the gap limit",
            )
        activity = text(sample.get("activity"), "Soak activity")
        require(activity in durations, "Unknown soak activity")
        if activity == previous_activity:
            durations[activity] = max(durations[activity], at - period_start)
        else:
            period_start = at
        previous = at
        previous_activity = activity
        require(sample.get("service") == "healthy", "Unhealthy soak sample")
        pressure = _object(sample.get("pressure"), "Soak pressure")
        for field in ("cpu_some_pct", "memory_some_pct", "io_some_pct"):
            percent = pressure.get(field)
            require(
                isinstance(percent, (int, float))
                and not isinstance(percent, bool)
                and 0 <= percent <= 100,
                f"Invalid soak pressure: {field}",
            )
    require(previous == end, "Soak sample coverage must end at the window boundary")
    for activity, duration in durations.items():
        minimum = window.get(f"minimum_{activity}_seconds")
        if type(minimum) is not int or minimum <= 0:
            raise Rejected(f"Approved {activity} minimum must be a positive integer")
        require(
            duration >= minimum, f"Soak {activity} period below the approved minimum"
        )


def _verify_profile(
    profile: str, report: dict[str, Any], expected: dict[str, str], reviewer: str
) -> None:
    require(report.get("profile") == profile, f"{profile}: report profile mismatch")
    for field, value in expected.items():
        require(report.get(field) == value, f"{profile}: {field} mismatch")
    require(report.get("reviewer") == reviewer, f"{profile}: unauthorized reviewer")
    operator = text(report.get("operator"), f"{profile}: operator")
    require(
        operator.strip().casefold() != reviewer.strip().casefold(),
        f"{profile}: reviewer must be independent",
    )
    cases = report.get("cases")
    if not isinstance(cases, list):
        raise Rejected(f"{profile}: cases must be a list")
    seen: set[str] = set()
    for raw in cases:
        case = _object(raw, f"{profile}: case")
        case_id = text(case.get("id"), f"{profile}: case ID")
        require(case_id not in seen, f"{profile}: duplicate case {case_id}")
        require(
            case.get("status") == "passed", f"{profile}: case {case_id} did not pass"
        )
        text(case.get("observation"), f"{profile}: case {case_id} observation")
        seen.add(case_id)
    require(seen == PROFILE_CASES[profile], f"{profile}: missing or unknown cases")


def verify_adoption(
    policy: dict[str, Any], evidence: dict[str, Any], root: Path
) -> list[str]:
    expected = {
        field: text(policy.get(field), field)
        for field in ("candidate_sha", "environment", "run_id")
    }
    require(
        re.fullmatch(r"[0-9a-f]{40}", expected["candidate_sha"]),
        "Invalid candidate SHA",
    )
    profiles = _object(policy.get("profiles"), "Selected profiles")
    require(
        profiles and profiles.keys() <= PROFILE_CASES.keys(),
        "Select known adoption profiles",
    )
    reports = _object(evidence.get("reports"), "Adoption evidence index")
    require(reports.keys() == profiles.keys(), "Missing or unexpected adoption reports")
    used_paths: set[Path] = set()
    for profile, identity in profiles.items():
        reviewer = text(identity, f"{profile}: authorized reviewer")
        reference = _object(reports[profile], f"{profile}: report reference")
        path = confined(root, text(reference.get("report"), f"{profile}: report"))
        require(path not in used_paths, "Adoption report reused across profiles")
        used_paths.add(path)
        digest = text(reference.get("sha256"), f"{profile}: report digest")
        require(
            re.fullmatch(r"sha256:[0-9a-f]{64}", digest),
            "Invalid adoption report digest",
        )
        report = read_adoption_record(path, digest)
        _verify_profile(profile, report, expected, reviewer)
        if profile == "remote":
            _verify_soak(report.get("soak"), policy.get("remote_window"))
    return sorted(profiles)
