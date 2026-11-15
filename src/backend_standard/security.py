"""Check scanner findings in addition to their process status."""

from typing import Any

from backend_standard.gates import Rejected


def reject_findings(report: Any, scanner: str) -> None:
    if scanner == "go":
        if not isinstance(report, list) or not any(
            isinstance(e, dict) and e.get("config") for e in report
        ):
            raise Rejected("Missing Go scanner configuration/report")
        if any(event.get("finding") for event in report):
            raise Rejected("Go vulnerability findings")
        return
    if scanner == "python":
        if not isinstance(report, dict) or not report.get("dependencies"):
            raise Rejected("Missing Python dependency inventory")
        if any(d.get("skip_reason") for d in report["dependencies"]):
            raise Rejected("Unscanned Python dependency")
        if any(dependency.get("vulns") for dependency in report["dependencies"]):
            raise Rejected("Python vulnerability findings")
        return
    if scanner == "dotnet":
        if not isinstance(report, dict) or not report.get("projects"):
            raise Rejected("Missing NuGet project inventory")

        def walk(value: Any) -> bool:
            if isinstance(value, dict):
                return bool(value.get("vulnerabilities")) or any(
                    walk(v) for v in value.values()
                )
            return isinstance(value, list) and any(walk(v) for v in value)

        if walk(report):
            raise Rejected("NuGet vulnerability findings")
        return
    raise Rejected("Unknown scanner")
