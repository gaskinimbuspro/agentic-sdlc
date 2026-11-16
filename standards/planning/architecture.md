# Architecture views and decisions

These controls are our policy, informed by the [architecture sources](sources.md#architecture). They extend [B01–B03](../backend/common.md) without changing them. Depth follows the project: a single small service needs a short record, not a document set.

| ID | Required control | Owner and acceptance evidence |
| --- | --- | --- |
| AR01 | Describe the system at the levels the project needs, using one consistent notation: system context, then containers (deployable or runnable units and data stores), then components only where a boundary must be enforced. Label every element with its responsibility and technology, and every relationship with its purpose. | Planner produces the views; independent reviewer checks them against requirements. Reject a diagram with unlabeled arrows, mixed abstraction levels or elements that no requirement needs. |
| AR02 | Record each significant decision as a short, numbered, immutable record with context, decision, status and consequences, including the alternatives considered. Supersede a record with a new one instead of rewriting it. | Planner writes; human accepts material trade-offs. Reject a framework, datastore, boundary or integration choice that appears only in code or chat. |
| AR03 | Start with one deployable unit with enforced internal module boundaries. Split a service only for a recorded need such as independent scaling, isolation, ownership or release cadence, and record the operational cost accepted with it. | Planner justifies each deployment unit in a decision record. Reject a new service, queue or datastore introduced without a requirement and a record. |
| AR04 | Turn each structural rule that matters into an automated check that fails the build: allowed dependencies between modules, forbidden imports, layering and public interfaces. Review what tooling cannot decide. | CI runs the checks; the Planner demonstrates that a deliberate violation fails. Reject a boundary that exists only as a folder name or a sentence. |
| AR05 | Keep views and records in the repository next to the code, generated or checked where practical. Update them in the change that alters the structure they describe. | Reviewer compares the candidate with the affected views and records. Reject a structural change that leaves the recorded view or decision false. |

## Relation to existing material

The [project profile](../backend/project-profile.template.json) already requires `architecture.decision_document` and `module_boundaries`; AR02 and AR04 define what those must contain. The reference's [architecture gate](../../reference/README.md#test-and-evidence-boundary) is a small example of AR04 and is not whole-program analysis. The repository's [draft diagrams](../../docs/diagrams/README.md) predate this standard and do not claim to follow AR01.
