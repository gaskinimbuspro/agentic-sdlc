"""Business input invariants independent of HTTP and persistence."""

import re


def customer_values(name: str, email: str) -> tuple[str, str]:
    name, email = name.strip(), email.strip().lower()
    if not 1 <= len(name) <= 100 or not 3 <= len(email) <= 254:
        raise ValueError("Invalid customer")
    if not re.fullmatch(
        r"[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+", email
    ):
        raise ValueError("Invalid customer")
    return name, email
