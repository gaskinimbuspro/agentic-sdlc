# Shared brief for method comparison

A tenant team needs a small customer directory so authorized members can add customer contacts and see existing contacts for their tenant. A tenant administrator delegates read and create permissions. Staff can enter the workflow from a trusted host session. The project brief describes behavior and leaves implementation technology to the compared planning method.

| ID | Required behavior and evidence |
| --- | --- |
| CR01 | A permitted member lists only the current tenant's customers. Verify populated, empty, failed and denied outcomes using separate tenant fixtures. |
| CR02 | A permitted member submits a name and email. Verify usable validation, exactly one customer with its audit entry, tenant-local duplicate rejection and no partial state on a known rollback. |
| CR03 | An anonymous, expired or unauthorized person cannot read or create. Verify server authorization independently of UI controls, including direct and cross-tenant actions. |
| CR04 | A member can cancel before submission or recover from an uncertain result without a blind repeat write. Verify visible and persisted effects separately. |
| CR05 | Users can complete in-scope flows with keyboard and assistive technology under a declared accessibility scope. Verify focus, errors, status announcements and narrow layouts. |
| CR06 | An operator verifies a clean build, actual integration tests, a safe migration, isolated recovery and candidate-bound review before release. Establish environment-specific performance and recovery targets before production use. |

The comparison excludes editing, deletion, arbitrary exports, bulk import and production identity provisioning. Select identifier/normalization, identity provider, tenant provisioning, retention, browser/device support, availability, performance and recovery objectives as explicit project decisions. Use the same decision gaps and cases for every method. The [backend reference](../reference/README.md) and [UI example](../standards/ui/examples/customer-admin/design.md) illustrate some resolved choices for the pilot while the brief remains technology-neutral.
