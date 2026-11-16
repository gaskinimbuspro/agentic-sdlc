# Agent delivery sources

Identified through search summaries on 16 November 2026. The network policy of the authoring session blocked these sites, so **the pages themselves were not opened in that session**. Inspect each page before a compliance or attribution claim relies on it. The controls in this standard are our policy and are not attributed to these publishers as requirements. Sources already inspected for the backend standard keep their entries in the [backend ledger](../backend/sources.md).

## Agent security

- OWASP GenAI Security Project, [Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), published December 2025. Risk categories ASI01–ASI10 including goal hijack through external content, tool misuse, identity and privilege abuse, supply chain, unexpected code execution and rogue agents. Informs AS01–AS07. No mapping to individual ASI entries is claimed.
- NIST, [SP 800-218A](https://csrc.nist.gov/pubs/sp/800/218/a/final), final July 2024. A secure-development community profile for generative AI and dual-use foundation models, used alongside SP 800-218. Informs AS05 and AS08. No conformity is claimed.
- Simon Willison, [The lethal trifecta for AI agents](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/). Private data, untrusted content and external communication combined in one agent. Informs the scope paragraph and AS01–AS03.

## Integration

- Martin Fowler, [Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html), already recorded as [F08](../backend/sources.md#f08).
- Pete Hodgson, published on martinfowler.com, [Feature Toggles](https://martinfowler.com/articles/feature-toggles.html). Toggle categories, lifetimes and the cost of leaving toggles in place. Attribute to Hodgson. Informs IN03 and IN04.
- Martin Fowler, [BranchByAbstraction](https://martinfowler.com/bliki/BranchByAbstraction.html). Making a large change gradually on the mainline. Informs IN03.
- DORA, [Trunk-based development](https://dora.dev/capabilities/trunk-based-development/) and [Working in small batches](https://dora.dev/capabilities/working-in-small-batches/). Capability descriptions associating short-lived branches and small changes with delivery performance. Informs IN01 and IN05; the numeric budgets are project decisions.

## Measurement

- DORA, [Software delivery performance metrics](https://dora.dev/guides/dora-metrics-four-keys/). Definitions of throughput and stability measures. Informs ME01.
- DORA, [2025 State of AI-assisted Software Development](https://dora.dev/research/2025/dora-report/). Survey findings that AI adoption relates to higher throughput and higher instability, and that existing engineering practices condition the result. Informs ME02–ME04. Survey associations are not predictions for one team.
- Anthropic and OpenAI engineering reports already recorded as [H01–H04](../backend/sources.md#h01). They motivate ME05 and ME06 as experience reports, not benchmarks.
