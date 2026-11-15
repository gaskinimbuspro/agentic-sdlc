# Customer administration design example

Status: illustrative, structurally reviewable design; not product approval, a running frontend or an accepted visual baseline. This example binds two screens to the existing [customer API](../../../../reference/openapi.json). It intentionally does not implement a login system, customer-detail endpoint, editing, deletion or production identity integration.

## Actors and outcomes

A member arrives from an already authenticated host application. R-UI-01: see only the current tenant's customers, including loading/empty/error/denied states. R-UI-02: create a valid customer, handle invalid/duplicate/unavailable and unconfirmed outcomes, and receive visible confirmation when creation succeeds. R-UI-03: cancel the create flow without making a request or persisting changes.

Production identity-provider/host integration and actual browser/runtime choices are explicit technical-readiness prerequisites. An unauthenticated state explains that the member must return to the host's session flow; a forbidden state offers safe recovery without exposing another tenant. This example does not authorize a worker to invent missing host behavior or turn synthetic API test credentials into browser production auth.

## Screens and states

| Screen | Route | Main behavior |
| --- | --- | --- |
| LIST | `/customers` | Heading, Add customer action, bounded list, loading indicator, empty explanation, actionable failure and safe access-denied/session-expired views. |
| CREATE | `/customers/new` | Labeled Name/Email fields, explicit Save/Cancel, validation feedback and safe server outcome handling. Tenant comes from the authenticated context and is never an editable authority grant. |

LIST supports default/loading/success/empty/error/forbidden/unauthenticated. CREATE supports default/loading/error/forbidden/unauthenticated and an unconfirmed-save state. Empty-result and success-as-a-separate-form-screen are N/A by declared design: an empty form is its default state and successful creation returns to LIST with feedback. These decisions await design acceptance along with the rest of the example.

The [packet](design-packet.json) enumerates every action, destination and API outcome, and the [wireframe](wireframes.svg) illustrates the two primary screens. These are low-fidelity layout references; design review must refine and accept the product's visual direction rather than treating the wireframe as a polished UI.

## Components and content

Use a shared page shell, page heading, primary/secondary actions, labeled text input, field error, error summary, status message and accessible customer table/list. The [tokens](tokens.json) record an illustrative palette/spacing/type scale; they have not been contrast-audited or accepted as branding. Control names are Add customer, Save customer and Cancel. Pending submission exposes status and prevents accidental duplicate submission; errors preserve safe input and focus correction appropriately. Cancel makes no create request.

At a narrow viewport, fields/actions stack and list content remains usable without dropping required data. Keyboard order follows reading order. Route changes expose the new page title/heading; recovery does not trap focus. Manual zoom, keyboard, assistive-technology and responsive evaluation remain required in the actual application.

## Contract and failure behavior

`GET /customers` handles 200 populated/empty, 400 invalid query, 401 expired/invalid identity, 403 denied scope and 503 unavailable dependency. A request ending without an HTTP response shows a recoverable list error with a bounded explicit retry. `POST /customers` handles 201 success, 400 invalid input, 401/403 identity/access, 409 canonical-email conflict, 413 body limit and 503 unavailable dependency. Use safe explanations for these failures.

On 201, show a confirmation based on the returned customer and refresh the ID-ordered, bounded list. Keep the confirmation visible during the refresh and through a recoverable list failure in the same session/tenant. The new row may fall outside the returned page. If the create request ends without an HTTP response, explain that it may already have committed, retain safe input and disable repeat submission from the unconfirmed state. Back to customers refreshes the list without sending another create request. Absence from the bounded list cannot establish whether the original request committed. Any stronger reconciliation needs a separately accepted API and transaction policy.

The browser must not receive an HMAC signing key or synthesize identity/tenant permissions. Session state and cache are cleared/revalidated on logout/tenant changes under the eventual accepted host binding. Listing is bounded by the existing API limit; this example does not imply unsupported cursor pagination or detail routes.

## Review and implementation evidence

Run `uv run --no-sync ui-standard design standards/ui/examples/customer-admin/design-packet.json` for structural reviewability. Test entries in the packet are expected cases, not passed executions. Implement the completed frontend profile before running component, real browser/backend, visual, automated/manual accessibility and budget checks. Product/visual acceptance and independent candidate review remain separate controls.
