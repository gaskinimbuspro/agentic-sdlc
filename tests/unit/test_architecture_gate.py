import pytest

from backend_standard.architecture import check_domain, check_transport
from backend_standard.gates import Rejected


@pytest.mark.parametrize(
    "language,source",
    [
        ("python", "from fastapi import Request"),
        ("go", 'package domain\nimport "net/http"'),
        ("dotnet", "using Npgsql;"),
    ],
)
def test_rejects_direct_domain_boundary_violations(language, source):
    with pytest.raises(Rejected):
        check_domain(language, source)


def test_rejects_sql_in_transport_adapter():
    with pytest.raises(Rejected):
        check_transport('handler: connection.execute("SELECT id FROM customers")')
