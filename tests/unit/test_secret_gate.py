import pytest

from backend_standard.secrets import findings


@pytest.mark.parametrize(
    "value,kind",
    [
        ("ghp_" + "A" * 36, "github-token"),
        ("AKIA" + "A" * 16, "aws-access-key"),
        ("-----BEGIN " + "PRIVATE KEY-----", "private-key"),
    ],
)
def test_blocks_known_credentials_without_returning_values(value, kind):
    assert findings(value) == [kind]
    assert value not in str(findings(value))


def test_environment_names_are_not_credentials():
    assert findings('required("JWT_KEY")') == []
