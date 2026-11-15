package main

import (
	"context"
	"errors"
	"time"

	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"
)

var errDuplicate = errors.New("duplicate customer")
var errStorage = errors.New("storage unavailable")

type customerStore struct{ pool *pgxpool.Pool }

func (s customerStore) create(ctx context.Context, tenant, name, email string) (customer, error) {
	name, email, err := customerValues(name, email)
	if err != nil {
		return customer{}, err
	}
	tx, err := s.pool.Begin(ctx)
	if err != nil {
		return customer{}, errStorage
	}
	defer func() {
		cleanup, cancel := context.WithTimeout(context.Background(), time.Second)
		defer cancel()
		_ = tx.Rollback(cleanup)
	}()
	id := newID()
	_, err = tx.Exec(ctx, "INSERT INTO customers VALUES ($1,$2,$3,$4)", id, tenant, name, email)
	if err == nil {
		_, err = tx.Exec(ctx, "INSERT INTO customer_audit(customer_id) VALUES ($1)", id)
	}
	if err == nil {
		err = tx.Commit(ctx)
	}
	if err != nil {
		var pg *pgconn.PgError
		if errors.As(err, &pg) && pg.Code == "23505" {
			return customer{}, errDuplicate
		}
		return customer{}, errStorage
	}
	return customer{id, tenant, name, email}, nil
}

func (s customerStore) list(ctx context.Context, tenant string, limit int) ([]customer, error) {
	if limit < 1 || limit > 100 {
		return nil, errInvalidInput
	}
	rows, err := s.pool.Query(ctx, "SELECT id::text,tenant_id::text,name,email FROM customers WHERE tenant_id=$1 ORDER BY id LIMIT $2", tenant, limit)
	if err != nil {
		return nil, errStorage
	}
	defer rows.Close()
	result := []customer{}
	for rows.Next() {
		var c customer
		if err := rows.Scan(&c.ID, &c.TenantID, &c.Name, &c.Email); err != nil {
			return nil, errStorage
		}
		result = append(result, c)
	}
	if rows.Err() != nil {
		return nil, errStorage
	}
	return result, nil
}
