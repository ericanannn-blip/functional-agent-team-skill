---
name: functional-agent-orchestration
description: Coordinate complex multi-step repository or operational work through functional roles, scoped delegation, verification, and independent review.
---

Use this for complex tasks that benefit from distinct research, planning, implementation, verification, or review. Follow repository `AGENTS.md` first. Select the smallest sufficient [workflow](references/workflows.md), record dependencies, and delegate only independent work in parallel.

The Orchestrator owns task state. Route domain expertise with [wshobson-router](../wshobson-router/SKILL.md); the router does not orchestrate. Give the Executor a plan and acceptance criteria. Send failed verification to the Analyst, then Planner before retrying. Review substantial changes independently after verification. Preserve approval boundaries in [permissions](references/permissions.md).

Read [roles](references/roles.md), [model policy](references/model-policy.md), [output contracts](references/output-contracts.md), [escalation](references/escalation.md), and [failure handling](references/failure-handling.md) only when those details are needed. Use [task template](templates/task.yaml) and [state template](templates/project-state.yaml) for durable handoffs.
