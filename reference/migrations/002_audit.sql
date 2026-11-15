CREATE TABLE customer_audit (
    customer_id uuid PRIMARY KEY REFERENCES customers(id),
    created_at timestamptz NOT NULL DEFAULT now()
);
