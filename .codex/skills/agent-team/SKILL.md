---
name: agent-team
description: Run a user task with a functional subagent team, automatically choosing and dispatching the roles needed for planning, implementation, verification, and review.
---

# Agent team

When invoked with a task, **run the task**. Act as the Orchestrator: choose the smallest useful workflow, create real subagents for the selected roles, collect their outputs, and finish the user's requested work. Do not merely describe a team, simulate role dialogue, or stop after a plan. A one-step task may need just one subagent; larger changes commonly need Planner, Executor, Verifier, and an independent Reviewer. Read the [workflow tiers](../functional-agent-orchestration/references/workflows.md) and [role contracts](../functional-agent-orchestration/references/roles.md) when choosing roles.

## Dispatch

1. Read the host repository's `AGENTS.md` and relevant files. Determine the goal, authorization, acceptance checks, dependencies, and any work already in progress. Host instructions and user scope take precedence over this skill.
2. Select roles by work required, not by a fixed number of agents. Use the [router](../wshobson-router/SKILL.md) only when specialist expertise changes the assignment; it chooses expertise and never manages the workflow. Use [risk check](../risk-check/SKILL.md) for consequential mutations.
3. If the host exposes a subagent creation tool, **call it** for each chosen role. Pass a scoped task, relevant paths/context, acceptance criteria, and the role's output contract. Tell each child to read the applicable role file from the host project's `.cursor/agents/<role>.md`, or from the installed user agent directory if the project has none. Do not assume spawning automatically loads these files. Give the child its own concrete deliverable, not the whole open-ended task.
4. Wait for dependent roles before dispatching their successors. Parallelize only independent work and respect tool concurrency limits. Keep edits to shared files under one owner at a time. Integrate child outputs into one task state and continue until the requested deliverable is complete.
5. Give Executor an approved scope, plan, and acceptance criteria. For substantial changes, dispatch Verifier for real checks and Reviewer for an independent review after verification. A failed check goes to Analyst, then Planner, before a scoped Executor retry. Follow the [failure handling](../functional-agent-orchestration/references/failure-handling.md); do not loop blindly.
6. Report what each dispatched role actually did, the evidence, unresolved limits, and the final result. A role named in a plan is not evidence that a subagent ran.

Use [model policy](../functional-agent-orchestration/references/model-policy.md) only where the host can select a child model. Model preferences never expand tool permissions or authorization. When subagent tools are unavailable, continue the task directly and state that no subagents were started; do not claim automatic delegation succeeded.
