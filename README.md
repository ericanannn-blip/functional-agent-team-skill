# Functional Agent Team Skill

A reusable Codex team workflow built from functional roles, a metadata-based specialist router, and small supporting skills. It is independent of any application or deployment project.

## Contents

| Path | Purpose |
| --- | --- |
| `.codex/skills/agent-team/` | Single chat entrypoint that selects roles and dispatches subagents |
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
Use $agent-team to implement a small change. Choose the needed subagents yourself, verify the result, and return the finished work.
```

The router can work from bundled metadata without downloading upstream prompts. To load full selected specialist instructions, supply a clean local checkout of `wshobson/agents` at the catalog's exact `source_commit`. See [the operational guide](docs/FUNCTIONAL_AGENTS.md).

For use across local projects, install all six skill folders into `%USERPROFILE%\.codex\skills\` and the eight role files into `%USERPROFILE%\.cursor\agents\`. Check destination names before copying so existing personal configuration is preserved. The skill links remain inside the installed skill set; the standalone repository remains the source of truth.

Model preferences are dispatch policy, not enforced by agent frontmatter. The actual model and tool permissions come from the host when each agent is invoked.
