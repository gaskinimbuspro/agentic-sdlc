# UI and database design research

Recorded 21 November 2026. Three research passes behind the [UI design process](../standards/ui/design-process.md), [schema design](../standards/operations/schema-design.md) and [discovery questionnaire](../standards/planning/discovery.md). The per-source ledgers are in the [UI](../standards/ui/sources.md) and [operations](../standards/operations/sources.md) source files; this record keeps what does not belong in a standard.

## Evidence boundary

Most cited web pages were read in full; some Nielsen Norman Group articles were read as summary and headings. Books were not read: Karwin (*SQL Antipatterns*, table of contents only), Ambler and Sadalage (*Refactoring Databases*, catalog names only), Kleppmann, Celko, Date, Cooper, Norman, Krug and Patton. No rule rests on a book's chapter content. Material Design's own navigation pages and Shopify Polaris pattern pages could not be read. No tool was installed or tried; vendor claims and prices are the vendors' own.

## Who the authorities are

| Area | Used as authority | Role in the standards |
| --- | --- | --- |
| UI structure | Jesse James Garrett's five planes | Order of design decisions (UX01); he says it is not a process, so the gating is ours |
| UI research and patterns | Nielsen Norman Group | Navigation, tables, empty states, loading, confirmation, notifications, heuristic review |
| UI patterns and forms | GOV.UK Design System, IBM Carbon | Validation, error recovery, state patterns |
| Tokens and scales | Design Tokens Community Group 2025.10, Atlassian | Token format and spacing scale |
| Schema and migrations | Sadalage and Fowler, PostgreSQL documentation and wiki | Evolution, types, constraints, row security |
| Indexing and paging | Markus Winand | Composite order, keyset pagination |
| Normalisation | Codd, Kent | Normal forms and justified denormalisation |
| Ownership | Fowler, Richardson | No shared database across modules or services |

## Disagreements between sources

- **Form validation timing.** GOV.UK validates on submit unless research supports inline validation; Wroblewski's 2009 study of 22 participants favoured inline validation for difficult fields. The standard requires the project to record its choice.
- **Spacing grids.** Sources agree on a limited scale with a base unit but not on one scale. The standard requires a scale, not a specific one.
- **Process.** Garrett's planes, Atomic Design and GOV.UK's phases each deny being a linear process. The ordered stages of the questionnaire are our policy.
- **Role-based navigation.** No source read prescribes it. UX02 is our own rule.
- **Table naming and bare `id`.** The SQL Style Guide differs from common PostgreSQL practice. The standard requires one recorded convention.

## AI design tools

| Tool | Output | Fit |
| --- | --- | --- |
| Polymet | A hosted React and Tailwind application; paid code export; one screen state per Figma export | Not on the critical path. It produces no screen, state and action specification, its agent overlaps both design and implementation roles, and its terms train on customer content by default with opt-out by email. Usable at most for throwaway exploration. |
| v0, Lovable, Bolt | Application code | Same overlap with the implementer role; accessibility audits of generated output reported failures. |
| Figma Make | Prototype inside Figma | Fits only where Figma is already the source of truth. |
| Google Stitch | Screens plus an open `DESIGN.md` token specification with lint | The specification is interesting; the product is experimental. |
| Subframe | A visual canvas that maps deterministically to React components in the repository | The closest fit if a visual tool is wanted; one-way sync and React only. |
| Claude Design | Designs and clickable prototypes | Matches "Voltran designs with the product owner"; a research preview. |

Decision recorded in UX05, UX12 and UX14: Voltran prepares the prototype, the product owner approves it, the Git design packet is the only source of truth, and the default component base is shadcn/ui on Tailwind with the component source given to the builder. Whether an open-weight builder follows current shadcn component APIs from memory is unverified, which is why the source is supplied.

## Reference schema findings

The static lint and review found five gaps in `reference/migrations`, listed in the [schema design standard](../standards/operations/schema-design.md#known-gaps-in-the-reference-schema). They are left in place and serve as real input that the lint rejects.

## Open items

- Integrate squawk and catalog checks for DD19, DD13 and DD17.
- PostgreSQL 19 was announced on 19 November 2026; the standards still pin 18.
- Extend the design packet schema to carry UX06–UX11 details so they can be validated instead of reviewed.
