# UI case matrix

Select applicable families from requirements and risk; document reasons for N/A and have them accepted independently. Map expected outcomes to actual tests, not only to a report count.

| ID | Family | Expected assertions |
| --- | --- | --- |
| UC01 | Primary journey | Correct visible result and intended persisted effect; every critical action has a destination. |
| UC02 | Form validation | Required/type/boundary/server errors, associated messages, focus and safe input preservation. |
| UC03 | Permissions/session | Anonymous/expired identity, denied role/tenant, logout/tenant switch and cache isolation; no forbidden data effects. |
| UC04 | Navigation/recovery | Deep link, refresh, back/forward, cancel, not-found and return behavior; accepted unsaved-input policy. |
| UC05 | Request/data states | Loading, empty, ready, failed, retry and duplicate action behavior; response contracts and conflicts. |
| UC06 | Keyboard/assistive technology | Names/roles/order, keyboard operation, modal focus/return and meaningful announcements under agreed scope. |
| UC07 | Responsive/content | Narrow/wide/zoomed layouts, long translated content, empty/max data and supported device orientation. |
| UC08 | Visual consistency | Accepted tokens/components and representative state differences under controlled rendering. |
| UC09 | Browser/locale | Supported engines, language/direction, time zones/numbers/dates and locale changes where applicable. |
| UC10 | Failure/security | Timeout/offline/malformed response, XSS-safe output, safe redirect/storage, conditional CSRF and sensitive-log protections. |
| UC11 | Performance | Recorded loading/interaction/stability and bundle/network budgets in the declared environment. |
| UC12 | Delivery evidence | Built-artifact smoke, current integration identity, nonempty suites, all required cases, redacted artifacts and independent verdict. |

The machine-checkable example maps all declared interaction outcomes to case IDs. Its small design does not instantiate every UC family. Screen-level manual evaluation, visual appearance and production behavior still need their own planned/actual evidence.
