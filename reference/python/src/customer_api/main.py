"""Synchronous handlers use FastAPI's worker pool; SQL never blocks its loop."""

import json
import os
import uuid
from typing import Annotated, Any

import jwt
import psycopg
from fastapi import Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from psycopg.rows import dict_row
from pydantic import BaseModel, ConfigDict, Field

from customer_api.domain import customer_values


def required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"Missing configuration: {name}")
    return value


JWT_KEY = required("JWT_KEY")
if len(JWT_KEY) < 32:
    raise RuntimeError("JWT_KEY must contain at least 32 characters")
DB = {
    "host": required("DB_HOST"),
    "port": required("DB_PORT"),
    "dbname": required("DB_NAME"),
    "user": required("DB_USER"),
    "password": required("DB_PASSWORD"),
    "connect_timeout": 3,
    "options": "-c statement_timeout=3000",
}
app = FastAPI(docs_url=None, redoc_url=None)


class Failure(Exception):
    def __init__(self, status: int) -> None:
        self.status = status


@app.exception_handler(Failure)
async def failure_handler(request: Request, exc: Failure) -> JSONResponse:
    return problem(exc.status)


def problem(status: int) -> JSONResponse:
    return JSONResponse(
        {"type": "about:blank", "title": "Request failed", "status": status},
        status_code=status,
        media_type="application/problem+json",
    )


@app.exception_handler(RequestValidationError)
async def invalid_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return problem(400)


@app.middleware("http")
async def request_boundary(request: Request, call_next: Any) -> Any:
    request_id = str(uuid.uuid4())
    # Buffer only up to the documented 8 KiB limit, including chunked bodies.
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 8192:
            return problem(413)
    request._body = bytes(body)
    try:
        response = await call_next(request)
    except Exception:
        response = problem(500)
    response.headers["X-Request-ID"] = request_id
    print(
        json.dumps(
            {
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "status": response.status_code,
            }
        ),
        flush=True,
    )
    return response


def identity(authorization: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise Failure(401)
    try:
        claims = jwt.decode(
            authorization[7:],
            JWT_KEY,
            algorithms=["HS256"],
            issuer="backend-reference",
            audience="customers",
            options={"require": ["exp", "iss", "aud", "sub", "tenant_id", "scope"]},
        )
        uuid.UUID(claims["tenant_id"])
        if not isinstance(claims["scope"], str):
            raise ValueError("Invalid scope")
        return dict(claims)
    except (jwt.PyJWTError, ValueError, TypeError, KeyError) as exc:
        raise Failure(401) from exc


class CreateCustomer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    tenant_id: Annotated[uuid.UUID, Field(strict=False)]
    name: str
    email: str


Identity = Annotated[dict[str, Any], Depends(identity)]


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "live"}


@app.get("/health/ready")
def ready() -> JSONResponse:
    try:
        with psycopg.connect(**DB) as conn:  # type: ignore[arg-type]
            conn.execute("SELECT 1")
        return JSONResponse({"status": "ready"})
    except psycopg.Error:
        return problem(503)


@app.post("/customers", status_code=201)
def create(body: CreateCustomer, claims: Identity) -> dict[str, str]:
    if (
        "customers:write" not in claims["scope"].split()
        or str(body.tenant_id) != claims["tenant_id"]
    ):
        raise Failure(403)
    try:
        name, email = customer_values(body.name, body.email)
    except ValueError as exc:
        raise Failure(400) from exc
    customer_id = str(uuid.uuid4())
    try:
        with psycopg.connect(**DB) as conn:  # type: ignore[arg-type]
            conn.execute(
                "INSERT INTO customers VALUES (%s, %s, %s, %s)",
                (customer_id, str(body.tenant_id), name, email),
            )
            conn.execute(
                "INSERT INTO customer_audit (customer_id) VALUES (%s)", (customer_id,)
            )
    except psycopg.errors.UniqueViolation as exc:
        raise Failure(409) from exc
    except psycopg.Error as exc:
        raise Failure(503) from exc
    return {
        "id": customer_id,
        "tenant_id": str(body.tenant_id),
        "name": name,
        "email": email,
    }


@app.get("/customers")
def customers(claims: Identity, limit: int = 20) -> list[dict[str, str]]:
    if "customers:read" not in claims["scope"].split():
        raise Failure(403)
    if not 1 <= limit <= 100:
        raise Failure(400)
    try:
        with psycopg.connect(**DB, row_factory=dict_row) as conn:  # type: ignore[arg-type]
            rows = conn.execute(
                "SELECT id::text, tenant_id::text, name, email FROM customers "
                "WHERE tenant_id = %s ORDER BY id LIMIT %s",
                (claims["tenant_id"], limit),
            ).fetchall()
        return [dict(row) for row in rows]
    except psycopg.Error as exc:
        raise Failure(503) from exc
