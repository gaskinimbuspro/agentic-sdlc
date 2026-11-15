#!/usr/bin/env python3
"""Protect the reference's declared domain files against direct boundary drift."""

from pathlib import Path

from backend_standard.architecture import check_domain, check_transport

root = Path(__file__).resolve().parents[1]
for language, relative in {
    "python": "reference/python/src/customer_api/domain.py",
    "go": "reference/go/domain.go",
    "dotnet": "reference/dotnet/CustomerApi/Domain.cs",
}.items():
    check_domain(language, (root / relative).read_text())
for relative in [
    "reference/python/src/customer_api/main.py",
    "reference/go/main.go",
    "reference/dotnet/CustomerApi/Program.cs",
]:
    check_transport((root / relative).read_text())
print("Reference domain dependency checks passed")
