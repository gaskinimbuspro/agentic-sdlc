import pytest

from backend_standard.gates import Rejected
from backend_standard.security import reject_findings


@pytest.mark.parametrize(
    "scanner,report",
    [
        ("python", {"dependencies": [{"vulns": [{"id": "synthetic-finding"}]}]}),
        (
            "go",
            [
                {"config": {"scanner_name": "govulncheck"}},
                {"finding": {"osv": "synthetic-finding"}},
            ],
        ),
        (
            "dotnet",
            {
                "projects": [
                    {
                        "frameworks": [
                            {
                                "transitivePackages": [
                                    {"vulnerabilities": [{"severity": "High"}]}
                                ]
                            }
                        ]
                    }
                ]
            },
        ),
    ],
)
def test_findings_reject_even_when_scanner_returns_zero(scanner, report):
    with pytest.raises(Rejected):
        reject_findings(report, scanner)


@pytest.mark.parametrize("scanner", ["python", "go", "dotnet"])
def test_empty_scanner_inventory_is_rejected(scanner):
    with pytest.raises(Rejected):
        reject_findings([] if scanner == "go" else {}, scanner)


@pytest.mark.parametrize(
    "scanner,report",
    [
        ("python", {"dependencies": [{"name": "known", "version": "1", "vulns": []}]}),
        ("go", [{"config": {"scanner_name": "govulncheck"}}]),
        (
            "dotnet",
            {
                "projects": [
                    {
                        "path": "reference.csproj",
                        "frameworks": [
                            {"framework": "net10.0", "topLevelPackages": []}
                        ],
                    }
                ]
            },
        ),
    ],
)
def test_clean_scanner_inventory_is_accepted(scanner, report):
    reject_findings(report, scanner)
