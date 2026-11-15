# Go backend profile v0.1

Apply with [common](../common.md) and [testing](../testing.md) rules. Select a supported stable toolchain. Prefer the standard library unless a framework/DI dependency has a concrete justification.

The executable [net/http binding](../../../reference/README.md) uses pinned Go, readonly modules, race detection, govulncheck, a compiled binary and real HTTP/PostgreSQL acceptance. The reference does not require a third-party HTTP framework.

| ID | Rule | Verification |
| --- | --- | --- |
| GO01 | Require gofmt and clear package names. Verification must reject formatting differences rather than silently modifying files. | Check gofmt output and exit status |
| GO02 | Use capability/dependency boundaries. Do not accumulate business behavior in utils or build class/interface layers per entity. | Dependency review and required structural checks |
| GO03 | Return/check ordinary errors, add context, and use errors.Is/As when identity matters. Avoid error-string matching and panic for normal business failures. | Negative tests, vet, and review |
| GO04 | Pass context.Context first where appropriate; propagate deadlines/cancellation to I/O. Do not use it as an optional-argument bag or generally store it in structs. | Cancellation/timeout tests and review |
| GO05 | Define small interfaces when needed, generally in the consumer. Do not add interfaces to every type merely to generate mocks. | Consumer/API design review |
| GO06 | Give goroutines an owner, termination path, and error handling. Manage channels/timers/shutdown and protect shared state. | Race detector and relevant concurrency/shutdown cases |
| GO07 | Commit go.mod/go.sum as needed. Reject tidy drift and use readonly build/test. Pin or explicitly govern automatic toolchain downloads. | Tidy diff, module verification, readonly commands |
| GO08 | Use testing and httptest; prefer table-driven tests for similar cases. Verify actual executed test events for each required suite. | Unit/API/integration results and counts |

Sources: [G01](../sources.md#g01), [G02](../sources.md#g02), [G03](../sources.md#g03), [G04](../sources.md#g04), [G05](../sources.md#g05), [G06](../sources.md#g06), [G07](../sources.md#g07). Feature organization and tool defaults are project policies.

## Command templates

```sh
format_output="$(gofmt -l .)" || exit "$?"
test -z "$format_output"
go mod tidy -diff
go mod verify
go vet -mod=readonly ./...
go build -mod=readonly ./...
go test -mod=readonly -count=1 -json ./...
go test -mod=readonly -count=1 -tags=integration -json ./tests/integration/...
go test -mod=readonly -count=1 -race -json ./...
```

Run each line as a separate checked step or in a fail-fast wrapper. `gofmt -l` does not itself fail on formatting differences; inspect output and preserve tool failures.

This layout places real-dependency tests under `tests/integration` with the integration build tag. The first test command excludes those files. Adapt actual package paths if the project chooses another layout. Report capture must preserve go test's exit status and count executed cases separately per required group.

Run race checks on a supported OS/architecture with the required C toolchain. An unsupported local run is blocked, not passed; complete it on an appropriate CI runner. The race detector only observes executed paths. [G04](../sources.md#g04).
