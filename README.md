# Functional Agent Team Skill

A reusable Codex team workflow built from functional roles, a metadata-based specialist router, and small supporting skills. It is independent of any application or deployment project.

## Contents

| Path | Purpose |
| --- | --- |
| `.cursor/agents/` | Eight functional project agents: Orchestrator, Researcher, Planner, Analyst, Executor, Verifier, Reviewer, and Router |
| `.codex/skills/functional-agent-orchestration/` | Workflow, model policy, permissions, output contracts, templates, and dispatch helper |
| `.codex/skills/wshobson-router/` | Source-pinned specialist metadata catalog and runnable router |
| `.codex/skills/{risk-check,editor,project-state}/` | Focused auxiliary skills |
| `scripts/` | Catalog builder, structure validator, and behavioral smoke tests |
| `docs/FUNCTIONAL_AGENTS.md` | Operational usage and extension guide |

## Quick start

From the project root, run with an available Python 3 executable:

```text
python scripts/validate_structure.py
python scripts/smoke_test.py
```

Then try a task in chat:

```text
Use functional-agent-orchestration to plan and implement a small change. Route specialist expertise only if needed, ask an independent Verifier to check acceptance criteria, and return the result for review.
```

The router can work from bundled metadata without downloading upstream prompts. To load full selected specialist instructions, supply a clean local checkout of `wshobson/agents` at the catalog's exact `source_commit`. See [the operational guide](docs/FUNCTIONAL_AGENTS.md).

Model preferences are dispatch policy, not enforced by agent frontmatter. The actual model and tool permissions come from the host when each agent is invoked.
