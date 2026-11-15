"""Transaction scripts and PostgreSQL details behind the application boundary."""

import uuid
from typing import TypedDict

import psycopg
from psycopg.rows import dict_row

from customer_api.domain import customer_values


class StoreConfig(TypedDict):
    host: str
    port: str
    dbname: str
    user: str
    password: str
    connect_timeout: int
    options: str


class DuplicateCustomer(Exception):
    pass


class StorageUnavailable(Exception):
    pass


class Store:
    def __init__(self, config: StoreConfig) -> None:
        self.config = config

    def ready(self) -> bool:
        try:
            with psycopg.connect(**self.config) as conn:
                conn.execute("SELECT 1")
            return True
        except psycopg.Error:
            return False

    def create(self, tenant: str, name: str, email: str) -> dict[str, str]:
        name, email = customer_values(name, email)
        identifier = str(uuid.uuid4())
        try:
            with psycopg.connect(**self.config) as conn:
                conn.execute(
                    "INSERT INTO customers VALUES (%s,%s,%s,%s)",
                    (identifier, tenant, name, email),
                )
                conn.execute(
                    "INSERT INTO customer_audit(customer_id) VALUES (%s)", (identifier,)
                )
        except psycopg.errors.UniqueViolation as error:
            raise DuplicateCustomer from error
        except psycopg.Error as error:
            raise StorageUnavailable from error
        return {"id": identifier, "tenant_id": tenant, "name": name, "email": email}

    def list(self, tenant: str, limit: int) -> list[dict[str, str]]:
        if not 1 <= limit <= 100:
            raise ValueError("Invalid list limit")
        try:
            with psycopg.connect(**self.config, row_factory=dict_row) as conn:
                rows = conn.execute(
                    "SELECT id::text,tenant_id::text,name,email FROM customers "
                    "WHERE tenant_id=%s ORDER BY id LIMIT %s",
                    (tenant, limit),
                ).fetchall()
            return [dict(row) for row in rows]
        except psycopg.Error as error:
            raise StorageUnavailable from error
