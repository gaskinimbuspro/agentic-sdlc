# Requirements

These controls are our policy, informed by the [requirement sources](sources.md#requirements). They govern the written input of every task. The Planner owns the text; the human owns product intent; the Implementer cannot change either to fit an implementation.

| ID | Required control | Owner and acceptance evidence |
| --- | --- | --- |
| RQ01 | Give every requirement a stable ID, one actor, one observable outcome and the reason it matters. Record scope and explicit non-goals for the project and for each task. | Planner writes, human accepts. Reject a requirement that names a screen or endpoint without an outcome, and a task without non-goals. |
| RQ02 | Before implementation, attach concrete examples to each behavior: given a state, when an action occurs, then an observable result and persisted effect. Include the important negative, boundary and permission examples, and the forbidden side effects. | Planner writes examples from requirements and maps them to case IDs. Reject a behavior whose only description is a general sentence, or an example copied from implementation output. |
| RQ03 | Write each example in one consistent, testable form selected for the project: Given/When/Then, or an EARS-style sentence with trigger, precondition and response. Use domain terms from a maintained glossary. | Independent reviewer checks that each example can be decided as passed or failed by observation. Reject wording such as "works correctly", "fast" or "user friendly" without a measurable result. |
| RQ04 | State quality targets as measurable scenarios with environment, load or condition, measure and threshold. Cover the relevant security, performance, availability, accessibility and data requirements. | Planner and human record targets or an explicit decision that none applies. Reject a target with no measurement method or environment. |
| RQ05 | Keep unresolved product, risk or contract decisions in a visible open-decision list with an owner. An affected task remains `draft`. The Implementer escalates a discovered gap and does not resolve it by assumption. | Coordinator readiness check and review of the open-decision list. Reject a ready task that depends on an open decision, and an implementation that settles one silently. |
| RQ06 | Version accepted requirements and examples. Change them only through a recorded decision that names affected tasks, tests and evidence. Existing review and evidence for affected behavior become stale. | Human accepts the change; Coordinator invalidates affected evidence. Reject an edited expected outcome in the same change that makes a failing test pass, unless a separate accepted requirement change exists. |

## Relation to existing rules

RQ01–RQ06 define the form of the inputs that [D01](../backend/definition-of-done.md), [T01](../backend/testing.md), [U01](../ui/common.md) and the [test case matrix](../backend/test-case-matrix.md) already require. They add no new completion gate. The [worked customer example](../backend/baseline-readiness.md#worked-acceptance-design-create-a-customer) shows examples with expected results and forbidden side effects in this form.

An example is evidence of intent, not of implementation. Passing generated tests does not show that the requirement was the right one; the human acceptance in RQ01 and the independent review remain necessary.
