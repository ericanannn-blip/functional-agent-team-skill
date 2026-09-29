---
name: project-state
description: Maintain a minimal durable task handoff record for multi-stage project work without storing conversation history or secrets.
---

Use the [state template](../functional-agent-orchestration/templates/project-state.yaml). Store only project, current goal and phase, completed work, decisions, files changed, known issues, open questions, next actions and last verified time. Mark unverified statements explicitly. Never store full conversation history or secrets; obey root `AGENTS.md` and existing work log rules.
