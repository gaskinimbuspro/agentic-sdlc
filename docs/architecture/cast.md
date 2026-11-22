# The cast

Every role in the [target architecture](README.md) has a name and an [avatar](../diagrams/assets/avatars/README.md), so that documents, diagrams and conversations refer to the same actor. The names are labels for roles. The products underneath keep their own names, and the standards keep their role names and rule IDs.

![The cast](../diagrams/08-cast.png)

| Character | Role | Runs as | Does | Never does |
| --- | --- | --- | --- | --- |
| **Gökhan** | Product Owner | A person | States the idea, decides product and risk questions, approves scope, requirements, design and merge | Reminds agents to run their checks |
| **Voltran** | Architect | Claude, called on demand | Runs discovery, writes requirements and architecture, prepares the UI packet, splits work into tasks | Writes the implementation |
| **Raymond** | Reviewer | Claude, in a separate session from Voltran | Reviews each pull request against the requirements and examples | Approves its own work, merges |
| **Debora** | Coordinator | A small Python program, run step by step by Argo Workflows ([details](iris.md)) | Picks a ready issue, opens a sandbox, starts Patrick with time and attempt limits, pushes the branch, opens the pull request | Makes product or design decisions; it is not a model |
| **Patrick** | Builder | Qwen Code driving a Qwen model, one sandbox per task | Implements one task with its tests, runs them, repairs failures, commits locally | Chooses tasks, pushes, holds git server credentials, changes its own rules |
| **McCall** | CI gate and release | Woodpecker on the work server's cluster, each step a pod | Runs the required checks on every pull request in a clean container; after a merge builds the image once and sets the staging digest | Gives opinions, waives a failure or deploys to the cluster |
| **Dembe** | Model server | vLLM on a rented GPU | Serves the pinned Qwen model to Patrick behind an API key | Holds source code or git credentials |
| **Teresa** | Mirror | Forgejo's push mirror | Copies project code to GitHub on a schedule as a backup | Carries issues, pull requests or CI; nobody develops on the copy |

**Forge** is Forgejo, the place where repositories, issues and pull requests live. It is a place, not an actor, so it has no character.

## Credentials

| Character | Holds | Does not hold |
| --- | --- | --- |
| Debora | A Forgejo token for the project repositories: read issues, push task branches, open pull requests | Merge rights, GitHub credentials, production access |
| Patrick | The model API key, inside its sandbox only | Any git server token |
| McCall | Read access to the repository it tests; on main only, the release token (registry push, staging overlay of the deploy repository) | Write access to protected branches, the prod overlay, cluster credentials |
| Argo CD (deployer, not a character) | Read-only access to deploy repositories; the only identity that changes the cluster | Write access to any repository |
| Teresa | A GitHub token limited to the mirror repositories | Anything else |
| Gökhan | Merge rights on protected branches | — |

Keeping push and pull-request rights with Debora instead of Patrick means injected text in an issue cannot make the model write to the git server directly ([AS01, AS02 and AS04](../../standards/agent-delivery/security.md)).

## Mapping to the standards

| Standard role | Character |
| --- | --- |
| Human / product owner | Gökhan |
| Backend Architect / Planner, UX Planner | Voltran |
| Independent Reviewer | Raymond |
| Coordinator | Debora |
| Implementer | Patrick |
| CI | McCall |

The product owner chose the names on 22 November 2026, after favourite characters from television and film: Raymond, Dembe, Patrick, Teresa, McCall and Debora. Only the first names are used, as labels; the avatars are generic drawings, not likenesses. Earlier drafts used Argus, Iris, Daedalus, Cerberus, Pythia and Echo for the same roles. The coordinator's program keeps its technical name `iris` (module, command, Kubernetes namespace, image and `iris/issue-N` branches), so commands and deployed workflows do not change. Rename a character here, in the diagram generator and in the avatar generator together.
