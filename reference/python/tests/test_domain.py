import pytest

from customer_api.domain import customer_values


def test_normalization() -> None:
    assert customer_values(" Ada ", " ADA@EXAMPLE.TEST ") == ("Ada", "ada@example.test")


@pytest.mark.parametrize(
    "name,email",
    [
        ("", "a@b.test"),
        ("a" * 101, "a@b.test"),
        ("Ada", "invalid"),
        ("Ada", "a@b"),
        ("Ada", "x" * 255),
    ],
)
def test_invalid_values(name: str, email: str) -> None:
    with pytest.raises(ValueError):
        customer_values(name, email)
