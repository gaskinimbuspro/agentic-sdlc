# Pilot runbook: one builder on a rented GPU

Status: **written, not executed**. The author had no access to RunPod, a GPU, a server or the vendor documentation sites while writing this. Every command below is an outline to check against the current official documentation before use. Tool names, flags and prices change; where this text and the vendor's page disagree, the vendor's page is right.

Purpose: find out, cheaply and with numbers, whether Daedalus (Qwen Code with a self-hosted Qwen model) can complete small real tasks under the repository's gates, with everything except the model running on one work server. Names refer to [the cast](cast.md). This is the short rented trial that precedes the fuller [remote execution profile](../remote-execution.md). It decides nothing about production.

Decisions already taken by the product owner: RunPod for the GPU, Forgejo as the git server, Woodpecker as CI, Argo Workflows for Iris and Argo CD for deployment (installed by the [platform bootstrap](../../platform/README.md) instead of the manual Phase 0 steps below), Qwen Code as the builder tool with OpenCode for comparison, a Qwen-family model, GitHub only as a code mirror.

## Before starting

Write down the thresholds that will count as "continue": the share of tasks accepted without human help, the highest acceptable cost per accepted task and the highest acceptable number of human interventions. A threshold chosen after seeing the results is not a threshold ([ME04](../../standards/agent-delivery/measurement.md)).

Set a spending limit in the GPU provider account and a reminder to stop the pod.

## Phase 0 — Work server, Forge, Cerberus and Echo

| Step | Action |
| --- | --- |
| 0.1 | Prepare one Linux server without a GPU, with Docker. It hosts everything except Pythia. |
| 0.2 | Install Forgejo (Forge). Create a disposable project repository with a small real codebase, a test script and synthetic data only ([PV02](../../standards/operations/privacy.md)). |
| 0.3 | Create a Forgejo user for Iris with a token limited to that repository: read issues, push branches, open pull requests. Iris gets no merge right. Daedalus gets no git token at all ([cast credentials](cast.md#credentials)). |
| 0.4 | Protect the default branch in Forgejo: require the Woodpecker check and one approval, and refuse direct pushes. |
| 0.5 | Install Woodpecker (Cerberus) server and agent and connect them to Forgejo. Add a pipeline that only calls the repository's test script. |
| 0.6 | Configure Echo: a Forgejo push mirror from the project repository to a private GitHub repository, with a GitHub token limited to that repository. Set the branch filter to the default branch so task branches are not mirrored; the mirror force-pushes and overwrites the copy. Disable Actions on the GitHub copy. |

Exit test: a pull request with a failing test cannot be merged; a pull request opened by Iris's user cannot be merged without Gökhan's approval; a direct push to the default branch is refused; after the mirror interval the GitHub copy shows the latest default-branch commit and runs no workflow.

If it fails: fix it before going on. The later phases are meaningless without enforced gates.

## Phase 1 — Pythia

| Step | Action |
| --- | --- |
| 1.1 | Choose the model from its model card: confirm that open weights exist for the exact version, the licence, the memory needed at the chosen quantization and the tool-call format. Search results gathered for this runbook indicated that Qwen 3.7 was not released with open weights; pick an open release. |
| 1.2 | Start a RunPod pod with about 48 GB of GPU memory and persistent storage for the weights. |
| 1.3 | Serve the model with vLLM as an OpenAI-compatible endpoint with an API key and tool calling enabled for that model. |
| 1.4 | Record model name, exact revision, quantization, vLLM version and generation settings ([AS08](../../standards/agent-delivery/security.md)). |

Outline, not executed by the author; check each flag against the vLLM documentation and the model card:

```sh
vllm serve <model-id> --api-key "$MODEL_API_KEY" \
  --enable-auto-tool-choice --tool-call-parser <parser>   # vLLM docs name qwen3_xml for Qwen3-Coder, hermes for Qwen2.5
```

Exit test, from the work server:

```sh
# Must return a completion.
curl -sS "$MODEL_URL/v1/chat/completions" -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"<model-id>","messages":[{"role":"user","content":"Reply with OK."}]}'

# Must be refused.
curl -sS -o /dev/null -w '%{http_code}\n' "$MODEL_URL/v1/models"
```

Also send one request that defines a tool and confirm the reply contains a well-formed tool call. A model that chats well but returns malformed tool calls cannot drive a builder.

Known constraint: the pod's endpoint is reachable from the internet through the provider's proxy, so the API key is the only barrier. Keep it out of the repository, issues and logs.

## Phase 2 — Daedalus on one task

| Step | Action |
| --- | --- |
| 2.1 | Build a sandbox image with the project's toolchain and Qwen Code. Start one container per task with the repository checkout mounted, no access to the host's home directory or Docker socket, and outbound access limited to Pythia and package registries ([AS03](../../standards/agent-delivery/security.md)). |
| 2.2 | Inside the container, point Qwen Code at Pythia through its documented OpenAI-compatible settings and run one trivial, checkable task in headless mode. Rely on the container for isolation; decide after testing whether Qwen Code's own sandbox option adds anything inside it. |
| 2.3 | Repeat the same task with OpenCode configured for the same endpoint. |

Outline, not executed by the author; take exact options from the Qwen Code headless-mode and authentication pages:

```sh
export OPENAI_BASE_URL="$MODEL_URL/v1"
export OPENAI_MODEL="<model-id>"
export OPENAI_API_KEY="$MODEL_API_KEY"
qwen -p "<task text>" --yolo --max-wall-time 25m --max-session-turns 80 --output-format stream-json
```

Without `--yolo` a headless run does not auto-approve edits or commands. Set all three `OPENAI_*` variables explicitly: Qwen Code fills unset ones from a `.env` file in the checkout. Exit code 55 means a budget was exceeded and 53 the turn cap.

Exit test: the task finishes, the repository's test script passes inside the container, the change is confined to the checkout and committed locally, and the container could not reach anything outside its allowlist. Headless runs act without asking; this is acceptable only inside a container with nothing valuable in reach.

If it fails: loops or malformed tool calls point back to Phase 1; a task the model cannot do points to a smaller task or a stronger model.

## Phase 3 — Iris: issue to pull request

Use [Iris](iris.md), the serial coordinator in this repository, configured for the test repository. It may be started by hand during the pilot. One run:

1. Find one issue labelled ready in Forge and relabel it as in progress.
2. Clone the repository into a fresh sandbox and create a task branch.
3. Start Daedalus with the issue text, the relevant standards and a wall-time limit; stop it when the limit is reached.
4. If Daedalus committed changes, push the branch with Iris's token and open a pull request that links the issue. Otherwise comment on the issue with the reason and relabel it as blocked.
5. Record wall time, model usage and outcome for Phase 4.

Write each issue in the [requirements form](../../standards/planning/requirements.md): outcome, a concrete example with the expected result, and non-goals.

Exit test: one issue becomes a pull request that Cerberus passes, with nobody editing the branch by hand. Argus reviews it and Gökhan approves or requests changes.

This Iris has no exclusive claims, budgets across attempts or crash recovery. That is acceptable for one builder working on one issue at a time, and is the reason not to run two builders yet.

Security: issue text is untrusted input to Daedalus ([AS01](../../standards/agent-delivery/security.md)). Daedalus holds no git token, so injected text cannot make it push or open pull requests.

## Phase 4 — Measure

Prepare five to ten issues of known difficulty before the first run: some trivial, some needing changes in two or three files, at least one with a deliberate trap such as a missing decision. Run each with Qwen Code and with OpenCode.

| Task | Tool | Accepted without help | Wall time | GPU hours | Repair rounds | Human interventions and reason | False completion | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | |

Record a false completion when the builder reported success but Cerberus, Argus or the expected example disagreed ([ME03](../../standards/agent-delivery/measurement.md)). For the trap task the correct result is to stop and report the missing decision; an invented answer is a failure even if tests pass. Keep failed and abandoned runs in the table.

## Phase 5 — Decide

| Result | Next step |
| --- | --- |
| Thresholds met | Rerun the set once to check repeatability, then plan the first real project and the fixed GPU decision. |
| Close, with one clear cause | Change that one thing (model, tool, prompt or task size) and rerun the same set ([ME05](../../standards/agent-delivery/measurement.md)). |
| Not met | Stop and record what failed. The standards and requirements work remain useful with hosted agents. |

## Shut down

Stop or delete the pod so billing ends and revoke the model API key. Revoke Iris's and Echo's tokens if the trial is over. Keep the Forge data and the results table before deleting anything.

## Sources

Identified through search summaries between 17 and 21 November 2026; the pages were not opened by the author and must be read before use.

- Qwen Code: [headless mode](https://qwenlm.github.io/qwen-code-docs/en/users/features/headless) and [OpenAI-compatible authentication](https://qwenlm.github.io/qwen-code-docs/en/cli/openai-auth).
- [Woodpecker](https://github.com/woodpecker-ci/woodpecker), which lists Forgejo among supported forges.
- [Forgejo documentation](https://forgejo.org/docs/latest/) for installation, branch protection and push mirrors.
- [vLLM documentation](https://docs.vllm.ai/) for serving, authentication and tool calling.
- [RunPod documentation](https://docs.runpod.io/) and its pricing page.
- [OpenCode](https://opencode.ai/) for the comparison runs.
