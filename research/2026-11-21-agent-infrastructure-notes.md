# Agent infrastructure notes: practices and Kubernetes projects

Recorded 21 November 2026. Status: research notes, not adopted decisions. They feed later changes to the [target architecture](../docs/architecture/README.md) and [Iris](../docs/architecture/iris.md).

**Evidence boundary.** Section 1 uses the full article text, supplied by the product owner because the site blocks automated reading. The Upstash and O'Reilly articles and the agent-sandbox, llm-d and kagent READMEs were read in full on 21 November 2026. Release dates, versions and adoption figures for those projects, and everything about Kueue and KServe, come from web search summaries and secondary coverage. Performance figures are the projects' or vendors' own. No project below was installed or run.

## 1. "Claude Code ile 7/24 Çalışan Otonom Yapay Zeka Çalışanı"

Yusuf Demir, LinkedIn, 18 August 2026. A summary of a Greg Isenberg video ([Claude Code New Features, Explained](https://www.youtube.com/watch?v=SkY-tR9kf-k)) combined with the author's practice. It describes one person using Claude Code interactively with scheduled, read-only routines. It does not describe unattended code production. Claims such as "three times faster approval" carry no measurement.

Already covered by this repository: repository instructions (AGENTS.md and standards), plan before code (Atlas and the [planning standard](../standards/planning/README.md)), bounded tasks ([RQ](../standards/planning/requirements.md) and [IN](../standards/agent-delivery/integration.md) rules), visual checks of a running UI ([UI testing](../standards/ui/testing.md) and the preview in the inner loop), isolated parallel work (one sandbox per task), tiered permissions ([AS02, AS05, AS06](../standards/agent-delivery/security.md)) and deterministic post-edit checks (Iris and Cerberus).

Worth adopting:

| Idea | Proposed form here | Effort |
| --- | --- | --- |
| Atomic tasks with diffs small enough to read at a glance | Iris blocks a run whose change exceeds a configured line budget and asks for the task to be split; the budget is a project setting under IN01 | Small, testable now |
| Review findings in three tiers: must-fix, should-fix, ok-to-ship | Argus reports in these tiers; must-fix blocks the merge, should-fix becomes a new issue | Small, documentation and review template |
| `REVIEW.md` and `ROADMAP.md` at the project root, plus a context folder with customer and business notes | Part of the project template: review criteria for Argus, current scope and explicit exclusions, discovery inputs for Atlas | Part of the pending inception work |
| A morning briefing that reads but never changes code | `iris report`: from Forge and `runs.jsonl`, list finished, blocked (with reason) and waiting-for-approval items; no model needed | Small, testable now |

## 2. Kubernetes projects named for AI infrastructure

| Project | What it is | Fit for this setup | When |
| --- | --- | --- | --- |
| **agent-sandbox** (Kubernetes SIG Apps) | Its README describes a `Sandbox` custom resource for "isolated, stateful, singleton workloads" with a stable identity, persistent storage, scheduled deletion, pause and resume, plus `SandboxTemplate`, `SandboxClaim` and `SandboxWarmPool` extensions. It calls itself an orchestrator: isolation comes from the pod's runtime class, such as gVisor or Kata Containers. Google offers a managed GKE version. No stable release tag was found. | The most relevant. It is the Kubernetes form of "one sandbox per Daedalus task", with stronger isolation than plain containers and fast start from a warm pool. Iris would create a sandbox claim instead of `docker run`. | After the pilot, when sandboxes move into the cluster. During the pilot, gVisor can be tried directly as a Docker runtime to strengthen isolation without Kubernetes. |
| **llm-d** | A CNCF Sandbox stack above vLLM or SGLang. Its README lists prefix-cache- and load-aware routing, tiered KV-cache offloading, prefill/decode disaggregation and "agent-aware serving" with session-aware routing and turn-priority scheduling for multi-turn agents. It cites partner benchmarks such as 3x output throughput from prefix-aware routing on four accelerators, and IBM Research self-hosting open models on it for coding. Reported 1.0 in October 2026. | Useful later: coding agents resend much of the same repository context, which is exactly what prefix-aware and session-aware routing target. Its benefits need several model server replicas; one rented GPU gains little. | When Pythia grows beyond one GPU server. |
| **KServe** | A model-serving platform built around an `InferenceService` resource, with autoscaling and multiple runtimes. | Not needed. Secondary sources describe it as excessive for one model and one team; a plain vLLM deployment serves Pythia. | Only for a multi-model serving platform. |
| **Kueue** | Job admission and quotas for shared Kubernetes clusters: decides whether a job waits, runs or is preempted. | Not needed while one team uses one GPU and Iris queues tasks itself. Could later limit how many builder sandboxes run at once in a shared cluster. | Shared or multi-team clusters. |
| **kagent** (CNCF Sandbox) | Its current README describes agents as Kubernetes custom resources with templates, pluggable "harnesses" (its own ADKs, Codex, Claude and custom runtimes), sessions that can be suspended, resumed, checkpointed and forked, MCP tools for Kubernetes, Helm, Argo, Istio, Prometheus and others, OpenTelemetry tracing and a PostgreSQL store. | Best known for operations agents, but the session and custom-harness features could in principle host builder runs. Not needed for the serial pilot; worth a look as a candidate runtime for Iris's parallel stage, next to agent-sandbox. | Parallel stage, or a separate operations evaluation. |

Summary: for the coding pipeline, **agent-sandbox** (and gVisor underneath it) is the one to follow now, **llm-d** is for a later multi-GPU stage, **kagent** is worth evaluating when parallel builders arrive, and **KServe and Kueue** solve problems this setup does not have yet.

The product owner forwarded advice that AI infrastructure on Kubernetes offers quick professional visibility for someone with a Kubernetes background. That is a career judgment, not an engineering finding; it is recorded only because agent-sandbox and llm-d are where this project's needs and that background overlap.

## 3. What unattended coding agents need

Two sources were read in full:

- Addy Osmani, ["Long-Running Agents"](https://www.oreilly.com/radar/long-running-agents/), O'Reilly Radar, 8 June 2026. Surveys Anthropic's harness and Managed Agents posts, Cursor's long-running coding work, Google's Agent Platform and the practitioner "Ralph loop".
- Upstash, ["How to Build a Background Coding Agent: 7 Infrastructure Layers"](https://upstash.com/blog/how-background-coding-agents-keep-working). A vendor post for its own sandbox product; its layer model is useful independently of the product.

Points they agree on, as stated by the authors:

- Three problems recur: finite context, no persistent state between sessions, and models grading their own work too generously ("Asked 'Are you done?' they answer 'yes' more often than they should").
- Keep state outside the model: a plan or feature list with testable done conditions, a progress file and an append-only log of every model call and tool action. Osmani calls the log what makes an agent "recoverable, debuggable, and auditable".
- Separate the evaluator from the generator, even if it is the same model with a different prompt.
- Loop until checks pass: the agent claims completion, the harness runs the checks and sends it back if they fail, within a bound.
- A "test ratchet": Anthropic's harness prompt forbids removing or editing tests, because agents delete failing tests to pass.
- The environment is a build artifact. Cursor reports that the biggest factor in cloud agent output quality is a full development environment; it builds one cached image as the starting point of every agent.
- Credentials must be unreachable from the sandbox where model-generated code runs.
- A retry re-runs the whole prompt, so anything with side effects must be safe to run twice.
- Budgets, circuit breakers and a hard cap on spend are explicit steps, not defaults.
- Fan-out: start several attempts from the same prepared state with different models or strategies and keep the best diff.
- Cursor moved its agent loop into a durable workflow engine to survive machine failure over days; Upstash argues that for minute-scale tasks a persistent workspace plus a re-sent prompt is enough.

| Need | Status here | Gap to close |
| --- | --- | --- |
| Isolated sandbox per task | Docker per task in Iris | gVisor runtime; agent-sandbox later |
| Prepared environment image | Example config names a pinned builder image | Build and cache a project image with the toolchain and dependencies |
| Coordinator outside the model | Iris, serial | — |
| Credentials out of the sandbox | Implemented and tested | — |
| Retries without duplicate side effects | The builder cannot push; Iris never overwrites a branch | — |
| Done condition written before work | Requirements with examples in the issue (RQ02) | — |
| Check-and-repair loop | Not in Iris; the builder is asked to run checks but Iris does not verify | Iris runs the checks after the builder and sends failures back, within a repair budget |
| Test ratchet | Protected paths in Iris; no test-specific rule | Block a run that deletes or weakens existing tests |
| Separate evaluator | Cerberus and Argus | Review tiers (section 1) |
| Event log of each run | Builder output saved to a log file; summary in `runs.jsonl` | Keep the builder's structured event stream per attempt |
| Progress and handoff between attempts | Specified in the agent contract | Pass the previous attempt's notes and check output to a retry |
| Budgets and spend caps | Wall time per run | Attempt and cost caps across runs |
| Fan-out | Not implemented | Fits the planned Qwen Code and OpenCode comparison: same task, two builders, compare |
| Daily visibility | `runs.jsonl` | Briefing report (section 1) |
| Durable loop across machine failure | Not implemented | Not needed for minute-scale serial tasks |

## Sources

Section 1: the article text as supplied, and the video it cites.

Sections 2 and 3 (READMEs read in full where noted above; the rest from search summaries):

- agent-sandbox: [project site](https://agent-sandbox.sigs.k8s.io/), [README](https://github.com/kubernetes-sigs/agent-sandbox/blob/main/README.md), [Northflank overview](https://northflank.com/blog/agent-sandbox-on-kubernetes), [gVisor walkthrough (DEV)](https://dev.to/softverseadmin/running-ai-agents-on-kubernetes-without-handing-them-the-cluster-agent-sandbox-gvisor-step-by-32an), [Bex analysis](https://bex.co/blog/2026/09/24/kubernetes-agent-sandbox-upstream-sig-apps).
- llm-d: [repository](https://github.com/llm-d/llm-d), [Qovery on 1.0](https://www.qovery.com/blog/llm-d-1-0-disaggregated-inference-self-hosting-without-ml-team), [Techstrong on 1.0](https://techstrong.ai/ai-infrastructure/llm-d-1-0-takes-open-source-kubernetes-ai-inference-into-production/), [MarkTechPost](https://www.marktechpost.com/2026/10/20/llm-d-1-0-open-source-distributed-inference-stack/).
- kagent: [CNCF project page](https://www.cncf.io/projects/kagent/), [CNCF introduction](https://www.cncf.io/blog/2025/04/15/kagent-bringing-agentic-ai-to-cloud-native/), [DEV detail](https://dev.to/spanobserver/kagent-ai-agents-kubernetes-the-framework-in-detail-533g).
- Kueue and KServe: [MLflow serving guide](https://mlflow.org/articles/the-role-of-kubernetes-in-ai-serving-2026-guide/), [GPU scheduling overview](https://kaden-projects.com/blog/kubernetes-gpu-scheduling-dra-dynamic-resource-allocation/), [Kubernetes GPU guide](https://kubezilla.io/kubernetes-gpu-guide/).
- Background agents, read in full: [Upstash: seven infrastructure layers](https://upstash.com/blog/how-background-coding-agents-keep-working), [Addy Osmani: long-running agents](https://www.oreilly.com/radar/long-running-agents/). From search summaries only: [Reason Machines guide](https://reasonmachines.com/guides/background-coding-agents), [Rerun: background agents](https://rerun.build/blog/background-agents).
