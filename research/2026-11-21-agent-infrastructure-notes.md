# Agent infrastructure notes: practices and Kubernetes projects

Recorded 21 November 2026. Status: research notes, not adopted decisions. They feed later changes to the [target architecture](../docs/architecture/README.md) and [Iris](../docs/architecture/iris.md).

**Evidence boundary.** Section 1 uses the full article text, supplied by the product owner because the site blocks automated reading. The Upstash and O'Reilly articles and the agent-sandbox, llm-d and kagent READMEs were read in full on 21 November 2026. Release dates, versions and adoption figures for those projects, and everything about Kueue and KServe, come from web search summaries and secondary coverage. Performance figures are the projects' or vendors' own. No project below was installed or run.

## 1. "Claude Code ile 7/24 Çalışan Otonom Yapay Zeka Çalışanı"

Yusuf Demir, LinkedIn, 18 August 2026. A summary of a Greg Isenberg video ([Claude Code New Features, Explained](https://www.youtube.com/watch?v=SkY-tR9kf-k)) combined with the author's practice. It describes one person using Claude Code interactively with scheduled, read-only routines. It does not describe unattended code production. Claims such as "three times faster approval" carry no measurement.

Already covered by this repository: repository instructions (AGENTS.md and standards), plan before code (Voltran and the [planning standard](../standards/planning/README.md)), bounded tasks ([RQ](../standards/planning/requirements.md) and [IN](../standards/agent-delivery/integration.md) rules), visual checks of a running UI ([UI testing](../standards/ui/testing.md) and the preview in the inner loop), isolated parallel work (one sandbox per task), tiered permissions ([AS02, AS05, AS06](../standards/agent-delivery/security.md)) and deterministic post-edit checks (Iris and Cerberus).

Worth adopting:

| Idea | Proposed form here | Effort |
| --- | --- | --- |
| Atomic tasks with diffs small enough to read at a glance | Iris blocks a run whose change exceeds a configured line budget and asks for the task to be split; the budget is a project setting under IN01 | Small, testable now |
| Review findings in three tiers: must-fix, should-fix, ok-to-ship | Argus reports in these tiers; must-fix blocks the merge, should-fix becomes a new issue | Small, documentation and review template |
| `REVIEW.md` and `ROADMAP.md` at the project root, plus a context folder with customer and business notes | Part of the project template: review criteria for Argus, current scope and explicit exclusions, discovery inputs for Voltran | Part of the pending inception work |
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

## 4. Primary sources on agent harnesses

Read in full on 22 November 2026: Anthropic's [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (Justin Young), [Managed agents](https://www.anthropic.com/engineering/managed-agents) and [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps) (Prithvi Rajasekaran); Cursor's [Scaling long-running autonomous coding](https://cursor.com/blog/scaling-agents); Stripe's [Minions, part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) (Alistair Gray, 19 February 2026); OpenAI's [Harness engineering](https://openai.com/index/harness-engineering/) (Ryan Lopopolo, 11 February 2026); Addy Osmani's [Self-improving coding agents](https://addyosmani.com/blog/self-improving-agents/). All describe frontier hosted models. None discusses open-weight or local models, gives per-task success rates or publishes its reviewer prompts.

| Practice, as reported | Source | Consequence for this setup |
| --- | --- | --- |
| Workflows are state machines where a node is either deterministic code or an agent loop. Linting and pushing "don't invoke an LLM at all". | Stripe | Iris already owns clone, push and pull request. Add deterministic check nodes; keep only "implement" and "fix failures" as agent steps. |
| At most two CI rounds: push, one agent attempt to fix failures, second push, then back to a human, because of "diminishing marginal returns". Lint loops run locally before any push. | Stripe | Repair budget for Iris: local check loop first, then a small fixed number of repair rounds. |
| A new session should: confirm its directory, read progress notes and recent git log, read the task list, run the init script and a smoke test before new work, work on one feature, commit and write a progress note. | Anthropic harness | A fixed start-of-run ritual in Iris's prompt; a progress note per attempt passed to the next. |
| A feature list in JSON whose entries the agent may change only by flipping `passes`; and the rule "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality." | Anthropic harness | Iris, not the builder, records pass or fail. Add the sentence to the prompt and a deterministic guard on test files. |
| Self-evaluation fails: agents praise mediocre work. A separate evaluator is "far more tractable" to make skeptical. An untuned evaluator finds real issues and then approves anyway. Useful output is one PASS or FAIL per agreed criterion with file, line and cause. | Anthropic harness design | Argus reports per acceptance example, with location and cause; tune its prompt from cases where it approved despite findings. |
| The evaluator is worth its cost "when the task sits beyond what the current model does reliably solo". Reported runs: 20 minutes and $9 solo with a broken core feature; 6 hours and $200 with planner, generator and evaluator. | Anthropic harness design | A weaker local builder sits further from "reliable solo", so review matters more here, not less. |
| A planner that fixes deliverables and high-level design but not implementation detail, because wrong detail cascades. Generator and evaluator agree testable criteria before code is written. | Anthropic harness design | Matches Voltran and RQ02; keep issue text on outcomes and examples. |
| Credentials must not be reachable from the sandbox; in the coupled design "a prompt injection only had to convince Claude to read its own environment". Session log, harness and sandbox are separate so any one can die. | Anthropic managed agents | Already how Iris works. Keep the full event stream of each run outside the container. |
| Flat peer agents with locks collapsed ("twenty agents would slow down to the effective throughput of two or three") and became risk-averse; an integrator role became a bottleneck. Planners, independent workers and a judge worked. "The prompts matter more" than harness or model. Models differ by role. | Cursor | Confirms serial-first and the planner, worker, judge split. Choose the model per role by measurement. |
| One disposable machine per task from a warm pool, ready in about ten seconds with repositories cloned and caches warm; no production data or arbitrary egress, which is what allows running without confirmation prompts. | Stripe | Pre-built project image with dependencies; egress allowlist. |
| Almost all rules are scoped to subdirectories or file patterns; global rules are used "very judiciously". Agents get a small curated tool set. | Stripe | Path-scoped instruction files in project repositories; short global file. |
| A short AGENTS.md of roughly 100 lines as a map into versioned docs; freshness checked by linters and CI; "anything it can't access in-context while running effectively doesn't exist". | OpenAI | The project template's AGENTS.md should index, not contain, the adopted standards. |
| Architecture and taste rules are custom lints whose "error messages … inject remediation instructions into agent context". "When documentation falls short, we promote the rule into code". | OpenAI | The cheapest steering for a weak model: check scripts whose failure text says how to fix it. Applies AR04. |
| When a run fails, ask "what capability is missing, and how do we make it both legible and enforceable for the agent?" rather than retrying harder. | OpenAI | Is the ME06 loop. |
| Stop conditions for a loop: iteration cap, time cap, no new commit in N iterations, diff much larger than expected or touching files outside scope. A task taking ten times the norm is stuck. | Osmani | Diff budget and stall detection in Iris. |

## 5. Tool facts from documentation

Read in full on 22 November 2026; versions as the pages showed them. Nothing was executed.

**Qwen Code** ([headless](https://qwenlm.github.io/qwen-code-docs/en/users/features/headless), [sandbox](https://qwenlm.github.io/qwen-code-docs/en/users/features/sandbox), [authentication](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/auth)):

- Headless runs use `-p`. Without an approval mode, tool use is not auto-approved: add `--yolo` (or `--approval-mode yolo`). The docs recommend `--yolo` with budgets inside an ephemeral container and no Qwen sandbox there.
- Budgets exist: `--max-wall-time` (for example `30m`), `--max-session-turns`, `--max-tool-calls`. They are enforced cooperatively. Exit code 55 means budget exceeded, 53 turn cap, 52 configuration error, 130 interrupt.
- `--output-format json` is buffered until the end and lost if the process is killed; `stream-json` writes one event per line as it happens and ends with a `result` line carrying `is_error`, `usage` and `session_id`.
- `--continue` and `--resume <sessionId>` resume a session stored under `~/.qwen/projects/`.
- Exporting `OPENAI_API_KEY` selects OpenAI-compatible mode; `OPENAI_BASE_URL` and `OPENAI_MODEL` complete it. A `.env` file found from the working directory upwards fills any of these that the process has not set, so a checked-out repository could redirect the builder unless all three are set explicitly.
- `--safe-mode` ignores repository-supplied hooks, extensions, MCP servers and context files.
- A separate Linux tool sandbox (`tools.executionSandbox`, bubblewrap or Landlock) can close network access for tool commands while the CLI still reaches the model. Whether it works inside Docker or under gVisor is not stated.

**vLLM** ([tool calling](https://docs.vllm.ai/en/latest/features/tool_calling.html)): `--enable-auto-tool-choice` plus `--tool-call-parser`. The page names `qwen3_xml` for Qwen3-Coder models and `hermes` for Qwen2.5 and QwQ. There is no `qwen3_coder` parser on that page, contrary to an earlier search summary. With automatic tool choice, "arguments may occasionally be malformed"; `--tool-strict-level` sets a server-side floor whose support for these parsers is not stated.

**gVisor** ([install](https://gvisor.dev/docs/user_guide/install/), [Docker quick start](https://gvisor.dev/docs/user_guide/quick_start/docker/)): install `runsc` from the project's apt repository, which registers a Docker runtime; run with `docker run --runtime=runsc`. Needs Linux 5.6 or later. Compatibility and performance limits are on other pages that were not read.

**Woodpecker 3.20** ([Forgejo forge](https://woodpecker-ci.org/docs/administration/configuration/forges/forgejo), [cron](https://woodpecker-ci.org/docs/usage/cron)): Forgejo support is built in and configured with `WOODPECKER_FORGEJO`, `WOODPECKER_FORGEJO_URL` and an OAuth client id and secret. On one host, put the agent on Forgejo's Docker network and set Forgejo's `[webhook] ALLOWED_HOST_LIST=external,loopback`. Cron jobs are defined in repository settings with schedules such as `@every 5m` and matched by `event: cron`, so Iris could run as a scheduled pipeline.

**Forgejo** ([mirrors](https://forgejo.org/docs/latest/user/repo-mirror/), [protection](https://forgejo.org/docs/latest/user/protection/)): a push mirror runs periodically and can also sync when commits are pushed. It force-pushes and "will overwrite any changes in the remote repository". A branch filter limits what is pushed, for example `main` only. For GitHub it needs a fine-grained token with Contents permission on that one repository. Branch protection supports required approvals; requiring a Woodpecker status check is not described on the page read and must be confirmed on install. Issues can depend on other issues.

## 6. Ordered backlog from this research

Items 1 to 5 were implemented in Iris on 22 November 2026 and are covered by tests; the rest are open.

| # | Change | Where |
| --- | --- | --- |
| 1 | Run the project's check command after the builder; on failure start a repair run with the failing output, up to a small fixed number of rounds | Iris |
| 2 | Block runs that delete or edit existing tests, or exceed a diff budget in lines or files | Iris |
| 3 | Refuse to start unless every builder variable is set, so a repository `.env` cannot redirect the model endpoint; use `--safe-mode` | Iris |
| 4 | Use `--yolo`, Qwen Code's own budgets and `stream-json`; keep the event stream per attempt; map exit codes 55 and 53 to clear blocked reasons | Iris configuration |
| 5 | Write a progress note per attempt and give it to the next attempt | Iris |
| 6 | `iris report` daily briefing | Iris |
| 7 | Tiered, per-criterion review output for Argus | Review template |
| 8 | Project template: short AGENTS.md as a map, REVIEW.md, ROADMAP.md, context folder, check script with remediation messages, pre-built builder image | Project template |
| 9 | gVisor as the sandbox runtime; mirror filter limited to the default branch | Pilot runbook |

## Sources

Section 1: the article text as supplied, and the video it cites.

Sections 2 and 3 (READMEs read in full where noted above; the rest from search summaries):

- agent-sandbox: [project site](https://agent-sandbox.sigs.k8s.io/), [README](https://github.com/kubernetes-sigs/agent-sandbox/blob/main/README.md), [Northflank overview](https://northflank.com/blog/agent-sandbox-on-kubernetes), [gVisor walkthrough (DEV)](https://dev.to/softverseadmin/running-ai-agents-on-kubernetes-without-handing-them-the-cluster-agent-sandbox-gvisor-step-by-32an), [Bex analysis](https://bex.co/blog/2026/09/24/kubernetes-agent-sandbox-upstream-sig-apps).
- llm-d: [repository](https://github.com/llm-d/llm-d), [Qovery on 1.0](https://www.qovery.com/blog/llm-d-1-0-disaggregated-inference-self-hosting-without-ml-team), [Techstrong on 1.0](https://techstrong.ai/ai-infrastructure/llm-d-1-0-takes-open-source-kubernetes-ai-inference-into-production/), [MarkTechPost](https://www.marktechpost.com/2026/10/20/llm-d-1-0-open-source-distributed-inference-stack/).
- kagent: [CNCF project page](https://www.cncf.io/projects/kagent/), [CNCF introduction](https://www.cncf.io/blog/2025/04/15/kagent-bringing-agentic-ai-to-cloud-native/), [DEV detail](https://dev.to/spanobserver/kagent-ai-agents-kubernetes-the-framework-in-detail-533g).
- Kueue and KServe: [MLflow serving guide](https://mlflow.org/articles/the-role-of-kubernetes-in-ai-serving-2026-guide/), [GPU scheduling overview](https://kaden-projects.com/blog/kubernetes-gpu-scheduling-dra-dynamic-resource-allocation/), [Kubernetes GPU guide](https://kubezilla.io/kubernetes-gpu-guide/).
- Background agents, read in full: [Upstash: seven infrastructure layers](https://upstash.com/blog/how-background-coding-agents-keep-working), [Addy Osmani: long-running agents](https://www.oreilly.com/radar/long-running-agents/). From search summaries only: [Reason Machines guide](https://reasonmachines.com/guides/background-coding-agents), [Rerun: background agents](https://rerun.build/blog/background-agents).

## Observed in the sandbox trial, 21 November

These are our observations on a temporary cluster, not vendor claims; details are in the [platform trial](../platform/README.md#what-was-tested-and-where).

- Forgejo branch protection can require the Woodpecker status context (`ci/woodpecker/pr/<workflow>`), which the Forgejo page read above did not describe. Required approval does not by itself stop the pull request author from merging; a merge allow-list does.
- Forgejo's `unprotected_file_patterns` lets an identity without push rights push changes that touch only the listed files. This gives the release bot a direct path to the staging overlay while every other change, prod included, needs a pull request.
- A Woodpecker secret limited to push events is refused to pull-request pipelines with an explicit error, so agent-written pipeline changes cannot read the release token before a merge.
- The Woodpecker kaniko plugin now ships the osscontainertools fork of kaniko and accepts `extra_opts`, which carries `--digest-file` for recording the built digest.
