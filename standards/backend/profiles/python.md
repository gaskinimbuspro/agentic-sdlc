# Python backend profile v0.1

Apply with [common](../common.md) and [testing](../testing.md) rules. Default tools are uv, Ruff, mypy, and pytest; pin their versions per project. This profile does not automatically select FastAPI, Django, or another web framework.

An executable [FastAPI binding](../../../reference/README.md) now demonstrates this profile with locked dependencies, a built/installed wheel, real HTTP/PostgreSQL acceptance, and CI. It is a selected reference framework, not a mandatory choice for every Python backend.

| ID | Rule | Verification |
| --- | --- | --- |
| PY01 | Base naming/readability on PEP 8. Use Ruff format/lint with this profile's 88-character width and explicit `E4,E7,E9,F,I,B,UP` lint selection. | Pinned formatter/linter and configuration |
| PY02 | Type production functions/interfaces and run mypy strict on `src`. Justify Any/ignores. Runtime input validation is separate. | mypy and malformed-input tests |
| PY03 | Record Python version, `pyproject.toml`, and `uv.lock`. Default to `src/<package>` plus `tests`; explain official framework layout adaptations. Test the installed project package. | Locked sync and correct package imports |
| PY04 | Keep business behavior independent of request/response objects. Select runtime validation and exception mapping for the framework. | Transport-independent and actual app-host tests |
| PY05 | Do not block the event loop with synchronous I/O. Use appropriate async APIs/worker boundaries; preserve cancellation and cleanup. | Timeout/cancellation and relevant concurrency cases |
| PY06 | Use defined expected exceptions. Catch broad exceptions only at suitable boundaries with observable handling/rethrow/mapping. Manage resources with context managers. | Error/cleanup tests and review |
| PY07 | Separate unit, app/API, and real-dependency tests. Default new projects to pytest importlib mode. Isolate fixtures and reject empty required suites. | Reports, exit codes, and executed counts |

Ruff/88, strict typing, package manager, and layout defaults are project choices. Sources: [P01](../sources.md#p01), [P02](../sources.md#p02), [P03](../sources.md#p03), [P04](../sources.md#p04), [P05](../sources.md#p05), [P06](../sources.md#p06), [P07](../sources.md#p07).

## Command templates

Bind these to real paths in the adopting project. Required suites must contain meaningful tests. Record a justified N/A scope rather than inventing a dummy test.

```sh
uv sync --locked --group dev
uv run --no-sync ruff format --check .
uv run --no-sync ruff check .
uv run --no-sync mypy --strict src
uv run --no-sync python -m pytest --import-mode=importlib tests/unit --junitxml=artifacts/unit.xml
uv run --no-sync python -m pytest --import-mode=importlib tests/integration --junitxml=artifacts/integration.xml
```

The dev group must contain tools/stubs; a src-layout package needs a configured build backend/package installation. Record Python/uv versions and lock other tools. `--no-sync` assumes a successful locked sync. Execute each command as a separate checked step or inside a fail-fast wrapper.

Specify framework startup/lifespan, test host, validation, migrations, and dependency fixtures before readiness. These templates do not create an application or CI pipeline.
