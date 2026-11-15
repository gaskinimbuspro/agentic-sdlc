CREATE TABLE customers (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL,
    name text NOT NULL CHECK (length(name) BETWEEN 1 AND 100),
    email text NOT NULL CHECK (length(email) BETWEEN 3 AND 254),
    CONSTRAINT customers_tenant_email UNIQUE (tenant_id, email)
);
