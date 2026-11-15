"""Synchronous handlers use FastAPI's worker pool; SQL never blocks its loop."""

import json
import os
import uuid
from typing import Annotated, Any

import jwt
from fastapi import Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response
from starlette.routing import Match

from customer_api.store import DuplicateCustomer, StorageUnavailable, Store, StoreConfig


def required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"Missing configuration: {name}")
    return value


JWT_KEY = required("JWT_KEY")
if len(JWT_KEY) < 32:
    raise RuntimeError("JWT_KEY must contain at least 32 characters")
DB: StoreConfig = {
    "host": required("DB_HOST"),
    "port": required("DB_PORT"),
    "dbname": required("DB_NAME"),
    "user": required("DB_USER"),
    "password": required("DB_PASSWORD"),
    "connect_timeout": 3,
    "options": "-c statement_timeout=3000",
}
storage = Store(DB)
app = FastAPI(docs_url=None, redoc_url=None)


class Failure(Exception):
    def __init__(self, status: int) -> None:
        self.status = status


@app.exception_handler(Failure)
async def failure_handler(request: Request, exc: Failure) -> JSONResponse:
    return problem(exc.status)


def problem(status: int) -> JSONResponse:
    response = JSONResponse(
        {"type": "about:blank", "title": "Request failed", "status": status},
        status_code=status,
        media_type="application/problem+json",
    )
    if status == 401:
        response.headers["WWW-Authenticate"] = "Bearer"
    return response


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
    response = problem(exc.status_code)
    response.headers.update(exc.headers or {})
    if exc.status_code == 405:
        methods: set[str] = set()
        for route in app.routes:
            if (
                isinstance(route, APIRoute)
                and route.matches(request.scope)[0] != Match.NONE
            ):
                methods.update(route.methods or set())
        response.headers["Allow"] = ", ".join(sorted(methods))
    return response


@app.exception_handler(RequestValidationError)
async def invalid_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return problem(400)


@app.middleware("http")
async def request_boundary(
    request: Request, call_next: RequestResponseEndpoint
) -> Response:
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


# JWT claims are heterogeneous boundary data; used identity fields are checked below.
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
        claims["tenant_id"] = str(uuid.UUID(claims["tenant_id"]))
        if (
            not isinstance(claims["scope"], str)
            or not isinstance(claims["sub"], str)
            or not claims["sub"]
        ):
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
    return JSONResponse({"status": "ready"}) if storage.ready() else problem(503)


@app.post("/customers", status_code=201)
def create(body: CreateCustomer, claims: Identity) -> dict[str, str]:
    if (
        "customers:write" not in claims["scope"].split()
        or str(body.tenant_id) != claims["tenant_id"]
    ):
        raise Failure(403)
    try:
        return storage.create(str(body.tenant_id), body.name, body.email)
    except ValueError as exc:
        raise Failure(400) from exc
    except DuplicateCustomer as exc:
        raise Failure(409) from exc
    except StorageUnavailable as exc:
        raise Failure(503) from exc


@app.get("/customers")
def customers(claims: Identity, limit: int = 20) -> list[dict[str, str]]:
    if "customers:read" not in claims["scope"].split():
        raise Failure(403)
    if not 1 <= limit <= 100:
        raise Failure(400)
    try:
        return storage.list(claims["tenant_id"], limit)
    except StorageUnavailable as exc:
        raise Failure(503) from exc
