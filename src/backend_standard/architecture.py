"""Reference-specific direct dependency checks, not whole-program analysis."""

import ast
import re

from backend_standard.gates import Rejected


def check_domain(language: str, source: str) -> None:
    if language == "python":
        for node in ast.walk(ast.parse(source)):
            imports = []
            if isinstance(node, ast.Import):
                imports = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imports = [node.module or ""]
            if any(name != "re" for name in imports):
                raise Rejected(
                    "Reference Python domain imported an undeclared dependency"
                )
    elif language == "go":
        imports = re.findall(r'"([^"\n]+)"', source)
        if any(
            name in {"net/http", "database/sql"} or name.startswith("github.com/")
            for name in imports
        ):
            raise Rejected("Reference Go domain imported a transport/data dependency")
    elif language == "dotnet":
        if re.search(
            r"\b(Npgsql|DbContext|DbConnection|HttpContext|HttpRequest)\b|Microsoft\.AspNetCore",
            source,
        ):
            raise Rejected("Reference .NET domain uses a transport/data dependency")
    else:
        raise Rejected("Unsupported architecture binding")


def check_transport(source: str) -> None:
    if re.search(r"\b(SELECT|INSERT INTO|DELETE FROM|UPDATE|CREATE TABLE)\b", source):
        raise Rejected("Reference HTTP adapter contains a direct SQL statement")
