# Pilot runbook: one agent on a rented GPU

Status: **written, not executed**. The author had no access to RunPod, to a GPU or to the vendor documentation sites while writing this. Every command below is an outline to check against the current official documentation before use. Tool names, flags and prices change; treat a mismatch with the vendor's page as the vendor being right.

Purpose: find out, cheaply and with numbers, whether a self-hosted open model driven by an existing agent runtime can complete small real tasks under the repository's gates. It is the rented, short trial that precedes the fuller [remote execution profile](../remote-execution.md). It decides nothing about production.

Decisions already taken by the product owner: RunPod for the pilot GPU, OpenHands as the runtime to try, a model from the Qwen family, and an existing tool rather than a new coordinator.

## Before starting

Write down, before any run, the thresholds that will count as "continue": the share of tasks accepted without human help, the highest acceptable cost per accepted task, and the highest acceptable number of human interventions. A threshold chosen after seeing the results is not a threshold ([ME04](../../standards/agent-delivery/measurement.md)).

Set a spending limit in the GPU provider account and a calendar reminder to stop the pod.

## Phase 0 — Test repository and identities

| Step | Action |
| --- | --- |
| 0.1 | Create a new, disposable repository with a small real codebase, a test suite and a CI workflow that runs it. Use synthetic data only ([PV02](../../standards/operations/privacy.md)). Do not use a client repository. |
| 0.2 | Create a GitHub App for the agent, installed on that repository only, with the smallest permissions that let it read contents and write branches, pull requests and issue comments. This is the implementing identity ([AS04](../../standards/agent-delivery/security.md)). |
| 0.3 | Protect the default branch: require the CI check, require one approving review, and disallow direct pushes. Do not let the App bypass these rules. |
| 0.4 | Keep your own account as the approving identity. If Claude reviews, it reports to you and you submit the approval, or it uses a second, separate identity. |

Exit test: a pull request opened by the App cannot be merged without your approval and a passing check; a direct push to the default branch by the App is refused.

Why this matters: GitHub does not let the author of a pull request approve it. If the agent opens pull requests with your token, nothing technical separates the writer from the approver, and [D08](../../standards/backend/definition-of-done.md) holds only as a promise.

If it fails: fix the protection rules before going on. The later phases are meaningless without them.

## Phase 1 — Model endpoint

| Step | Action |
| --- | --- |
| 1.1 | Choose the model from its model card: confirm that open weights exist for the exact version, the licence, the memory needed at the chosen quantization, and the tool-call format it expects. Search results gathered for this runbook indicated that Qwen 3.7 was not released with open weights; confirm on the publisher's page and pick an open release. |
| 1.2 | Start a RunPod pod with about 48 GB of GPU memory and persistent storage for the weights. |
| 1.3 | Serve the model with vLLM as an OpenAI-compatible endpoint, with an API key and with tool calling enabled for that model. |
| 1.4 | Record the model name, exact revision, quantization, vLLM version and generation settings ([AS08](../../standards/agent-delivery/security.md)). |

Outline, not executed by the author; verify every flag against the vLLM documentation and the model card:

```sh
vllm serve <model-id> --api-key "$MODEL_API_KEY" \
  --enable-auto-tool-choice --tool-call-parser <parser-named-by-the-model-card>
```

Exit test, run from another machine:

```sh
# Must return a completion.
curl -sS "$MODEL_URL/v1/chat/completions" -H "Authorization: Bearer $MODEL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"<model-id>","messages":[{"role":"user","content":"Reply with OK."}]}'

# Must be refused.
curl -sS -o /dev/null -w '%{http_code}\n' "$MODEL_URL/v1/models"
```

Also send one request that defines a tool and confirm the reply contains a well-formed tool call. A model that answers chat but returns malformed tool calls cannot drive an agent.

Known constraint: the pod's endpoint is reachable from the internet through the provider's proxy, so the API key is the only barrier. Keep the key out of the repository, issues and logs. The private-network placement in the [target architecture](README.md#where-it-runs) is not available in this trial.

If it fails: try the parser the model card names, then a different open model. Do not go on with unreliable tool calls.

## Phase 2 — One agent, one task

| Step | Action |
| --- | --- |
| 2.1 | Use a machine with Docker that is **not** the GPU pod: a small rented server or your own computer. The runtime starts a sandbox container per task. Whether Docker runs inside a RunPod pod was not verified; assume it does not. |
| 2.2 | Install OpenHands as its documentation describes and run it in headless mode against the test repository checkout. |
| 2.3 | Point it at the model endpoint. The documented variables are `LLM_MODEL`, `LLM_BASE_URL` and an API key variable; use the model name form the documentation gives for an OpenAI-compatible server. |
| 2.4 | Give it one trivial, checkable task, for example adding a small function with a test. |

Outline, not executed by the author; take the actual command from the OpenHands headless-mode page:

```sh
export LLM_MODEL="openai/<model-id>"
export LLM_BASE_URL="$MODEL_URL/v1"
export LLM_API_KEY="$MODEL_API_KEY"
# then the headless command from the official documentation, with the task text
```

Exit test: the task finishes, the repository's tests pass, and the change is confined to the checkout. Check that the sandbox cannot read the host's home directory or credentials ([AS03](../../standards/agent-delivery/security.md)). Note that headless mode approves the agent's actions automatically; this is acceptable only inside a sandbox with nothing valuable in reach.

If it fails: read the event log. Loops and malformed tool calls point back to phase 1; a task the model cannot do points to a smaller task or a stronger model.

## Phase 3 — Issue to pull request

| Step | Action |
| --- | --- |
| 3.1 | Add the OpenHands GitHub Action to the test repository, configured with the App's credentials and the model endpoint as repository secrets. |
| 3.2 | Write one issue in the [requirements form](../../standards/planning/requirements.md): the outcome, a concrete example with expected result, and non-goals. |
| 3.3 | Trigger the agent the way the Action's documentation describes; at the time of writing that was the `fix-me` label or a comment addressed to the agent. |
| 3.4 | Let CI run on the pull request. Review it yourself or with Claude, then approve or request changes. |

Exit test: one issue becomes a pull request that passes CI without anyone editing the branch by hand.

This arrangement is the coordinator for the serial stage: the issue list is the queue, the Action starts the agent, and branch protection enforces the gates. It has no exclusive claims, budgets or recovery. That is acceptable for one agent working on one issue at a time and is the reason not to run two agents yet.

Security: issue and comment text is untrusted input to the agent ([AS01](../../standards/agent-delivery/security.md)). On a public repository anyone can write an issue; restrict who can apply the trigger, and keep the App's permissions to this repository.

## Phase 4 — Measure

Prepare five to ten issues of known difficulty before the first run: some trivial, some needing changes in two or three files, at least one with a deliberate trap such as a missing decision. Run each once.

| Task | Accepted without help | Wall time | GPU hours | Repair rounds | Human interventions and reason | False completion | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

Record a false completion when the agent reported success but CI, review or the expected example disagreed ([ME03](../../standards/agent-delivery/measurement.md)). For the trap task, the correct result is that the agent stops and asks; an invented answer is a failure even if tests pass.

Keep failed and abandoned runs in the table.

## Phase 5 — Decide

Compare the table with the thresholds written before starting.

| Result | Next step |
| --- | --- |
| Thresholds met | Run the same set once more to check repeatability, then plan the first real project and the fixed GPU decision. |
| Close, with one clear cause | Change that one thing (model, prompt, task size) and rerun the same set ([ME05](../../standards/agent-delivery/measurement.md)). |
| Not met | Stop. Record what failed. The standards and requirements work remain useful with hosted agents. |

## Shut down

Stop or delete the pod so billing ends, revoke the model API key, and uninstall or suspend the GitHub App if the trial is over. Delete the test repository only after the results table has been saved elsewhere.

## Sources

Identified through search summaries between 17 and 20 November 2026; the pages were not opened by the author and must be read before use.

- OpenHands documentation: [headless mode](https://docs.all-hands.dev/usage/how-to/headless-mode), [GitHub Action](https://docs.openhands.dev/usage/how-to/github-action), [local models](https://docs.openhands.dev/openhands/usage/llms/local-llms) and [environment variables](https://docs.openhands.dev/openhands/usage/environment-variables.md).
- [vLLM documentation](https://docs.vllm.ai/) for serving, authentication and tool calling.
- [RunPod documentation](https://docs.runpod.io/) and its pricing page for current pod types and rates.
- GitHub documentation on [installation tokens](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app) and branch protection.
