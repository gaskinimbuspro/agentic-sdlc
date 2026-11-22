# Open-source agentic development tooling: what fits our platform

Date: 22 November 2026. Question from the product owner: which projects on GitHub could help our agentic delivery setup (Forgejo, k3s, Woodpecker, Argo Workflows and Argo CD, a self-hosted Qwen builder, Claude for planning and review).

## Method and limits

Candidates were found through GitHub repository search (stars, licence and last push read from the search API on this date) and the author's knowledge of the field. For each candidate below, the claims about features come from its README, read on this date, unless marked otherwise. Nothing was installed or run. A README describes what a project says it does; each item still has to be tried before adoption. Licences marked `NOASSERTION` by GitHub were not resolved here.

Fit is judged against our constraints: Forgejo as the git server, everything self-hosted, no agent holding merge or deploy rights, deterministic gates, and a local Qwen model through an OpenAI-compatible endpoint.

## Ledger

| Project | Stars, licence, last push | Read | What it says it does | Fit for us |
| --- | --- | --- | --- | --- |
| [kodustech/kodus-ai](https://github.com/kodustech/kodus-ai) | 1.6k, AGPL-3.0 (README badge), 2026-11-21 | README | Self-hosted AI code review; "reviews pull requests on GitHub, GitLab, Bitbucket, Azure DevOps, and Forgejo"; any OpenAI-compatible endpoint or Anthropic; Docker on a VM; telemetry opt-out with `KODUS_TELEMETRY_DISABLED=true`. | Strong candidate for Argus's line-level review. Unverified: whether it can act as a required status check and judge a task's acceptance criteria. |
| [The-PR-Agent/pr-agent](https://github.com/The-PR-Agent/pr-agent) | 16.5k, MIT, 2026-11-20 | README | "Community-maintained legacy project of Qodo"; git providers include Gitea; models through LiteLLM. Moved from `qodo-ai/pr-agent`; Docker images now under `pragent/pr-agent`. | Lighter alternative to Kodus, run as a job. Forgejo is not named; Gitea API compatibility would have to be tried. |
| [Nikita-Filonov/ai-review](https://github.com/Nikita-Filonov/ai-review) | 0.6k, Apache-2.0, 2026-11-21 | README | Runs in CI; inline, context and summary reviews; Gitea among VCS integrations; Claude, Ollama and others. | Second alternative; smaller project. |
| [BerriAI/litellm](https://github.com/BerriAI/litellm) | 63.7k, not resolved, 2026-11-22 | README | Self-hosted AI gateway: "virtual keys, spend tracking, guardrails, load balancing"; vLLM supported as a provider. | One gateway in front of Pythia (vLLM) and the Claude API: one key per agent, budgets, a log of every call. Licence of the enterprise parts to be checked. |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | 37.7k, MIT badge, 2026-11-22 | README | Self-hosted observability and evals for LLM calls: traces, usage and cost. | Measures cost and time per task for [ME01–ME04](../standards/agent-delivery/measurement.md). |
| [binwiederhier/ntfy](https://github.com/binwiederhier/ntfy) | 35.7k, Apache-2.0 and GPLv2, 2026-11-20 | README | Push notifications by HTTP PUT/POST; self-hostable; open-source Android and iOS apps. | The planned "needs you" notifications. |
| [renovatebot/renovate](https://github.com/renovatebot/renovate) | 23.2k, AGPL-3.0, 2026-11-22 | Source tree | Dependency update pull requests; has `forgejo` and `gitea` platform modules (`lib/modules/platform/forgejo`). | Dependency updates arrive as ordinary pull requests through our gates, with no model involved. |
| [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | 31.2k, MIT, 2026-10-28 | Metadata | Secret scanning. | A Woodpecker step on every pull request; agents must never commit a secret. |
| [semgrep/semgrep](https://github.com/semgrep/semgrep) | 17.9k, LGPL-2.1, 2026-11-20 | Metadata | Pattern-based static analysis. | Project-specific rules as a required check. |
| [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | 39.6k, Apache-2.0, 2026-11-20 | Metadata | Image and dependency vulnerability scanning. | Scan the image the release pipeline builds before staging. |
| [boxed/mutmut](https://github.com/boxed/mutmut), [stryker-mutator/stryker-js](https://github.com/stryker-mutator/stryker-js) | 1.6k BSD-3; 3.4k Apache-2.0 | Metadata | Mutation testing for Python and JavaScript/TypeScript. | Answers a gap Iris documents: its guard cannot tell a weakened assertion from a legitimate edit. A mutation score on changed code catches tests that assert nothing. |
| [oraios/serena](https://github.com/oraios/serena) | 31.6k, GPL-3.0-or-later badge, 2026-11-19 | README | MCP server with semantic code retrieval and editing through language servers; works with MCP clients such as OpenCode. | Could give Daedalus symbol-level navigation instead of reading whole files. Unverified with Qwen Code. |
| [rtk-ai/rtk](https://github.com/rtk-ai/rtk) | 87.4k, Apache-2.0 and BUSL-1.1, 2026-11-21 | README | Compresses command output an agent reads (test runs to failures only, compact git output). README itself warns that output reduction is not the same cut in cost. | Fewer tokens for a local model with a limited context. The BUSL part needs a licence check before use. |
| [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench), [harbor-framework/terminal-bench](https://github.com/harbor-framework/terminal-bench) | 6.2k MIT; 1.1k Apache-2.0 | Metadata | Benchmarks for coding agents on real issues and terminal tasks. | Compare Qwen candidates before the RunPod pilot, alongside our own task set. |
| [briandeheus/bakedpi](https://github.com/briandeheus/bakedpi) | 4 stars, MIT, 2026-09-21 | README | A daemon that polls Forgejo; agents (the pi coding agent) work on assigned issues, open pull requests and answer review comments; one agent session per issue, resumed when feedback arrives on its pull request. | Too small to adopt, but the closest design to ours. Its per-issue session resumed on review feedback is a model for our planned feedback loop. |
| [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | 94k, MIT, 2026-11-22 | README | Runs OpenHands or other agents locally, in Docker, on VMs or a server; any model. | Remains the builder fallback, as recorded earlier. |
| [github/spec-kit](https://github.com/github/spec-kit), [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD), [eyaltoledano/claude-task-master](https://github.com/eyaltoledano/claude-task-master) | 151k MIT; 55.6k; 28.5k | README (spec-kit), metadata | Specification-driven development and task breakdown for coding agents. | Overlap with our planning standards and task plan. Worth reading for template ideas; no reason to switch. |
| [obra/superpowers](https://github.com/obra/superpowers) | not in search results | README | Skills that trigger automatically: brainstorming, writing plans of 2–5 minute tasks, subagent-driven development with a review after each task. | Ideas for Daedalus's instructions and for Voltran's task size. Licence not checked. |
| [dagger/container-use](https://github.com/dagger/container-use), [e2b-dev/E2B](https://github.com/e2b-dev/E2B), [kubernetes-sigs/agent-sandbox](https://github.com/kubernetes-sigs/agent-sandbox) | 4.1k; 15k; 4.7k, all Apache-2.0 | README (container-use), metadata | Isolated environments for agents. | We isolate with one pod per step on Argo; agent-sandbox was already noted as the Kubernetes-native option to watch. |
| [BloopAI/vibe-kanban](https://github.com/BloopAI/vibe-kanban), [smtg-ai/claude-squad](https://github.com/smtg-ai/claude-squad), [OrchestratorInc/agent-orchestrator](https://github.com/OrchestratorInc/agent-orchestrator) | 28.8k Apache-2.0; 8.8k AGPL-3.0; 15k Apache-2.0 | README | Local cockpits for running several coding agents in parallel. | Personal tools for interactive work, not part of the 24/7 pipeline. |

## Our proposals, in order

These are recommendations, not decisions.

1. **Try Kodus for Argus** before writing our own reviewer: it names Forgejo, runs self-hosted and takes Claude as its model. Keep our own small gate only for what Kodus does not do: judging the task's acceptance criteria and reporting the required status.
2. **Put LiteLLM in front of every model call**, both Pythia and Claude: per-agent keys and budgets solve the key-handling and cost questions in one place. Its keys come from Bitwarden.
3. **Add cheap deterministic gates to the Woodpecker templates:** gitleaks on every pull request, Trivy on the release image, and mutation testing on changed code where the language has a tool.
4. **ntfy for notifications** and **Renovate for dependency updates**, both self-hosted and both already Forgejo-capable.
5. **Langfuse** once the pilot runs, to measure cost and time per accepted task.
6. **Before the RunPod pilot**, run a small SWE-bench or Terminal-Bench subset on the Qwen candidates, then our own tasks.
7. **Later, measured:** Serena and rtk to reduce what Daedalus reads; adopt only if the pilot shows a gain.
