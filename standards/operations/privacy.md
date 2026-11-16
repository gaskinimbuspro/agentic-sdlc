# Personal data and AI use

These controls are our policy, informed by the [privacy and governance sources](sources.md#privacy-and-ai-governance). They are engineering obligations, not legal advice. The applicable law, the lawful basis and any regulatory classification are determined for each project by its accountable owner with qualified advice. No compliance with any regulation or standard is claimed.

| ID | Required control | Owner and acceptance evidence |
| --- | --- | --- |
| PV01 | Record which personal data the system processes, for what purpose, on what recorded basis, where it is stored and who receives it. Link this to the dataset inventory in [DB01](database.md). | Data owner approves the record before affected implementation. Reject a new personal data field with no purpose or retention decision. |
| PV02 | Keep real personal data out of prompts, task packets, fixtures, test databases, logs, traces and evidence. Use synthetic data in development and tests. | CI and review check fixtures and retained artifacts. Reject production data copied into a development or agent environment. |
| PV03 | Record every external model or tool provider that receives project content, what it receives, where it is processed and its retention terms. Prefer a self-hosted model or a contractually bounded provider for confidential or personal content. | Human approves the provider list; operator shows workers cannot reach an unlisted provider under [AS03](../agent-delivery/security.md). Reject sending customer or confidential content to a provider that is not recorded. |
| PV04 | Implement access, correction, export and deletion for personal data where the project requires them, including replicas, exports and backup expiry under [DB01](database.md). | Engineering runs a deletion and export case against real storage and records what remains and until when. Reject a deletion that leaves the data in a secondary store without a recorded expiry. |
| PV05 | Keep a register of where AI is used in building and in the product, the decisions it influences, the human oversight applied and the assessed risk. Tell the client or user what the project decides must be disclosed. | Accountable owner reviews the register at project start and on material change. Reject an AI-made decision about a person with no recorded oversight. |

## Scope

Running models on owned hardware addresses the provider part of PV03 for those models. It does not address PV01, PV02, PV04 or PV05. Use the cited regulations and frameworks to decide what a project must do; this table only ensures the questions are asked and the answers are recorded before implementation.
