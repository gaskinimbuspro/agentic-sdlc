# Method comparison criteria

Compare BMad Method, AWS AI-DLC, and GitHub Spec Kit using the same brief. Tie answers to primary sources and pinned versions; an undocumented or untested capability is not a passed requirement.

| Area | Questions |
| --- | --- |
| Project input | Can it consume a separately prepared brief and surface missing/conflicting requirements? |
| Requirements | How are behavior, acceptance criteria, security, and operational targets specified? |
| Architecture | How are boundaries, data ownership, contracts, and decisions preserved and enforced? |
| Language profiles | How are Python/.NET/Go rules selected, checked, and upgraded? |
| Roles | Who decomposes tasks, dispatches them, implements, and independently reviews? |
| Context | Is one coding task scoped to one owner/workspace/context? How are retrieval, handoff, compaction, and budgets managed? |
| Readiness | What prevents ambiguous, dependency-blocked, or untestable tasks from being dispatched? |
| Dispatch | Are claims exclusive, retry-safe, and durable? What prevents duplicate work and conflicting parallel changes? |
| Repository setup | How are owner, visibility, naming, repository strategy, and bootstrap permissions determined? |
| Task tracking | Are requirements, dependencies, decisions, PRs, and evidence linked? Is GitHub integration built in or additional? |
| Testing | Are negative/authorization/data/resilience cases included and executed against real boundaries? |
| Completion | Can it reject empty reports, zero tests, stale SHAs, skipped required checks, and unresolved findings? |
| Diagrams | Can process/agent/project views remain editable, sourced, and consistent with implementation? |
| Operations | How are integration, release, recovery, permissions, observability, and state recovery handled? |
| Economics | What are total tokens/cost, repair loops, accepted-task latency, escaped defects, and manual interventions? |

A feature existing in documentation does not establish suitability. Keep documentation review and executed trial results separate.
