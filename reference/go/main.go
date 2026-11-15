package main

import (
	"context"
	"crypto/rand"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"regexp"
	"slices"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type customer struct {
	ID       string `json:"id"`
	TenantID string `json:"tenant_id"`
	Name     string `json:"name"`
	Email    string `json:"email"`
}

func required(name string) string {
	value := os.Getenv(name)
	if value == "" {
		panic("missing configuration: " + name)
	}
	return value
}

func newID() string {
	var b [16]byte
	if _, err := rand.Read(b[:]); err != nil {
		panic("random source unavailable")
	}
	b[6] = (b[6] & 15) | 64
	b[8] = (b[8] & 63) | 128
	return fmt.Sprintf("%x-%x-%x-%x-%x", b[:4], b[4:6], b[6:8], b[8:10], b[10:])
}

func respond(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(body); err != nil {
		slog.Warn("response_write_failed")
	}
}

func problem(w http.ResponseWriter, status int) {
	if status == 401 {
		w.Header().Set("WWW-Authenticate", "Bearer")
	}
	w.Header().Set("Content-Type", "application/problem+json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(map[string]any{"type": "about:blank", "title": "Request failed", "status": status})
}

func identity(w http.ResponseWriter, r *http.Request, key []byte, scope string) (string, bool) {
	header := r.Header.Get("Authorization")
	if !strings.HasPrefix(header, "Bearer ") {
		problem(w, 401)
		return "", false
	}
	token, err := jwt.Parse(strings.TrimPrefix(header, "Bearer "), func(t *jwt.Token) (any, error) { return key, nil },
		jwt.WithValidMethods([]string{"HS256"}), jwt.WithIssuer("backend-reference"),
		jwt.WithAudience("customers"), jwt.WithExpirationRequired())
	if err != nil || !token.Valid {
		problem(w, 401)
		return "", false
	}
	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok {
		problem(w, 401)
		return "", false
	}
	tenant, tok := claims["tenant_id"].(string)
	tenant = strings.ToLower(tenant)
	sub, sok := claims["sub"].(string)
	scopes, cok := claims["scope"].(string)
	if !tok || !sok || sub == "" || !cok || !regexp.MustCompile(`^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$`).MatchString(tenant) {
		problem(w, 401)
		return "", false
	}
	if !slices.Contains(strings.Fields(scopes), scope) {
		problem(w, 403)
		return "", false
	}
	return tenant, true
}

func routes(pool *pgxpool.Pool, key []byte) http.Handler {
	store := customerStore{pool: pool}
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) { problem(w, 404) })
	for _, path := range []string{"/customers", "/health/live", "/health/ready"} {
		mux.HandleFunc(path, func(w http.ResponseWriter, r *http.Request) {
			allow := "GET"
			if r.URL.Path == "/customers" {
				allow = "GET, POST"
			}
			w.Header().Set("Allow", allow)
			problem(w, 405)
		})
	}
	mux.HandleFunc("GET /health/live", func(w http.ResponseWriter, r *http.Request) { respond(w, 200, map[string]string{"status": "live"}) })
	mux.HandleFunc("GET /health/ready", func(w http.ResponseWriter, r *http.Request) {
		ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
		defer cancel()
		if err := pool.Ping(ctx); err != nil {
			problem(w, 503)
			return
		}
		respond(w, 200, map[string]string{"status": "ready"})
	})
	mux.HandleFunc("POST /customers", func(w http.ResponseWriter, r *http.Request) {
		tenant, ok := identity(w, r, key, "customers:write")
		if !ok {
			return
		}
		var input struct {
			TenantID string `json:"tenant_id"`
			Name     string `json:"name"`
			Email    string `json:"email"`
		}
		decoder := json.NewDecoder(http.MaxBytesReader(w, r.Body, 8192))
		decoder.DisallowUnknownFields()
		if err := decoder.Decode(&input); err != nil {
			var size *http.MaxBytesError
			if errors.As(err, &size) {
				problem(w, 413)
			} else {
				problem(w, 400)
			}
			return
		}
		if err := decoder.Decode(new(any)); err != io.EOF {
			problem(w, 400)
			return
		}
		input.TenantID = strings.ToLower(input.TenantID)
		if !regexp.MustCompile(`^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$`).MatchString(input.TenantID) {
			problem(w, 400)
			return
		}
		if input.TenantID != tenant {
			problem(w, 403)
			return
		}
		ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
		defer cancel()
		result, err := store.create(ctx, tenant, input.Name, input.Email)
		if err != nil {
			if errors.Is(err, errInvalidInput) {
				problem(w, 400)
			} else if errors.Is(err, errDuplicate) {
				problem(w, 409)
			} else {
				problem(w, 503)
			}
			return
		}
		respond(w, 201, result)
	})
	mux.HandleFunc("GET /customers", func(w http.ResponseWriter, r *http.Request) {
		tenant, ok := identity(w, r, key, "customers:read")
		if !ok {
			return
		}
		limit := 20
		if value := r.URL.Query().Get("limit"); value != "" {
			parsed, err := strconv.Atoi(value)
			if err != nil {
				problem(w, 400)
				return
			}
			limit = parsed
		}
		if limit < 1 || limit > 100 {
			problem(w, 400)
			return
		}
		ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
		defer cancel()
		result, err := store.list(ctx, tenant, limit)
		if err != nil {
			problem(w, 503)
			return
		}
		respond(w, 200, result)
	})
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		requestID := newID()
		w.Header().Set("X-Request-ID", requestID)
		slog.Info("http_request", "request_id", requestID, "method", r.Method)
		mux.ServeHTTP(w, r)
	})
}

func main() {
	slog.SetDefault(slog.New(slog.NewJSONHandler(os.Stdout, nil)))
	key := []byte(required("JWT_KEY"))
	if len(key) < 32 {
		panic("JWT_KEY too short")
	}
	endpoint := url.URL{Scheme: "postgres", Host: required("DB_HOST") + ":" + required("DB_PORT"), Path: required("DB_NAME"), User: url.UserPassword(required("DB_USER"), required("DB_PASSWORD"))}
	query := endpoint.Query()
	query.Set("sslmode", "disable")
	query.Set("connect_timeout", "3")
	query.Set("statement_timeout", "3000")
	endpoint.RawQuery = query.Encode()
	config, err := pgxpool.ParseConfig(endpoint.String())
	if err != nil {
		panic("invalid database configuration")
	}
	pool, err := pgxpool.NewWithConfig(context.Background(), config)
	if err != nil {
		panic("database pool unavailable")
	}
	defer pool.Close()
	server := &http.Server{Addr: "127.0.0.1:" + required("PORT"), Handler: routes(pool, key), ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 5 * time.Second, WriteTimeout: 10 * time.Second, IdleTimeout: 60 * time.Second, MaxHeaderBytes: 8192}
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	stopped := make(chan struct{})
	go func() {
		defer close(stopped)
		<-ctx.Done()
		deadline, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		_ = server.Shutdown(deadline)
	}()
	if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		panic("HTTP server failed")
	}
	<-stopped
}
