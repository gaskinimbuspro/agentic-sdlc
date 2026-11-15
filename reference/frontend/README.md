# Customer-admin frontend reference

This pilot binds the [customer-admin design](../../standards/ui/examples/customer-admin/design.md) to React, TypeScript, Vite and a real packaged FastAPI/PostgreSQL backend. The [profile](profile.json) records required commands, test environments and pending adoption evidence.

## Architecture and scope

The UI uses two routes, a small view/state layer and a typed HTTP adapter. Vite's preview server serves the built artifact on loopback. The test harness injects a short-lived synthetic token server-side and supplies the fixture's tenant ID. Browser requests contain no signing key or bearer token. Backend authorization and persistence remain authoritative.

The pilot supports listing, adding, duplicate feedback, cancellation and recovery from lost responses or uncertain writes. It keeps safe form input on correction, announces and focuses feedback, and verifies keyboard navigation and narrow layouts. The browser fault-injection case commits using the real API before delivering HTTP 503 to the UI, then verifies no second request occurs.

The fixture identity, preview server and default bounded list are appropriate to this controlled test. A production adopter specifies a real host session, auth and expiry flow, TLS, supported devices/locales, production monitoring and application release authority. Manual assistive-technology assessment and independently accepted visual baselines remain outstanding for application acceptance. The test artifacts support that review.

## Repeat verification

From this directory run `npm ci` under the pinned Node/npm versions, then run `npm run format`, `npm run lint`, `npm run types`, `npm run test`, `npm run security`, `npm run build` and `npm run budget`. The dependency check blocks moderate or higher findings. A pinned minimatch override resolves [GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249) in the linter; remove it when the upstream dependency resolves to a patched release. The budget measures combined gzip size of compiled JS/CSS with a 120 KiB limit. It does not measure browser interaction metrics.

The [frontend workflow](../../.github/workflows/frontend.yml) builds the app, packages the Python backend, provisions disposable PostgreSQL and runs Playwright Chromium, Firefox and WebKit. It uploads actual browser/component JUnit reports, a built-asset size measurement and representative screenshots. Browser communication, customer rows and audit effects are exercised against real persistence. Component tests isolate transport responses. Browser fault injection is scoped to list connection recovery and the response lost after a successful write.

The preview server is started by the isolated harness. To repeat full CI locally, install the locked backend tool environments and Playwright browsers, build and install the Python reference wheel in its own environment, then run `uv run --no-sync python scripts/reference_acceptance.py python --browser` from the repository root with Docker available.
