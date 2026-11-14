# Initial research sources

Access date: 14 November 2026. Record pinned versions before trials. Initial readings support comparison; they do not constitute adoption of a framework or a review of every author's books.

## Architecture and testing

Martin Fowler's [layering](https://martinfowler.com/bliki/PresentationDomainDataLayering.html), [evolutionary design](https://martinfowler.com/articles/designDead.html), [self-testing code](https://martinfowler.com/bliki/SelfTestingCode.html), [coverage](https://martinfowler.com/bliki/TestCoverage.html), and [CI](https://martinfowler.com/articles/continuousIntegration.html) explain key foundations. His catalog contains alternatives rather than one mandatory architecture.

Simon Brown's [modular monolith article](https://simonbrown.je/modular-monolith/) discusses component boundaries and enforcement. Mark Richards' [ADR lesson summary](https://www.developertoarchitect.com/lessons/lesson157.html) covers decision rationale and trade-offs; only the public text summary was inspected. [Kent Beck](https://kentbeck.com/) provides TDD/design and augmented-coding perspectives.

The detailed [backend source ledger](../standards/backend/sources.md) separates author contributions, official language/tool documentation, and our project choices.

## Agentic development approaches

- [SAP overview](https://www.sap.com/turkey/resources/what-is-agentic-development): concepts, planning/execution/feedback, tools, and governance; not a detailed implementation standard.
- [BMad Method](https://github.com/bmad-code-org/BMAD-METHOD): requirements, architecture/UX, task preparation, and delivery roles. At initial inspection the README distinguished stable v6.12 from v7 preview on main; do not mix release documentation.
- [AWS AI-DLC](https://github.com/awslabs/aidlc-workflows), [introduction](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/), and [adaptive workflows](https://aws.amazon.com/blogs/devops/open-sourcing-adaptive-workflows-for-ai-driven-development-life-cycle-ai-dlc/): lifecycle, context-sensitive depth, and human decisions. Older blog phase descriptions and current repository versions must be distinguished.
- [GitHub Spec Kit](https://github.com/github/spec-kit): principles, specifications, planning, tasks, and implementation verification. Pin a release/commit before comparison.

## Agent context and feedback

- [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents): focused context, retrieval, compaction, and durable notes.
- [Anthropic long-running harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents): incremental work, explicit functionality, tests, and handoffs.
- [Ryan Lopopolo / OpenAI harness engineering](https://openai.com/index/harness-engineering/): an engineering team's repository/environment/feedback experience.
- [Birgitta Böckeler](https://martinfowler.com/articles/harness-engineering.html): guides and sensors; cautions about relying only on AI-produced tests.
- [Kief Morris](https://martinfowler.com/articles/exploring-gen-ai/humans-and-agents.html): product outcomes and software delivery loops.
- [Rahul Garg](https://martinfowler.com/articles/reduce-friction-ai/): context, shared standards, and collaboration.
- [Naresh Jain](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html): a bounded experiment on cost/acceptance; not a universal production guarantee.

Articles hosted on Fowler's site are attributed to their actual authors. Vendor engineering reports inform hypotheses; cost and quality claims require a relevant pilot.
