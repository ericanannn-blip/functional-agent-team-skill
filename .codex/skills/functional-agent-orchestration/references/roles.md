# Functional roles

| Role | Responsibility | Mutation |
| --- | --- | --- |
| Orchestrator | Goal, decomposition, dependencies, delegation, integration, escalation | No direct implementation unless unavoidable |
| Researcher | Retrieve dated sources, compare evidence, expose contradictions | Read only |
| Planner | Scope, task graph, acceptance, rollback | Read only |
| Analyst | Hypotheses, root cause, trade-offs, uncertainty | Read only |
| Executor | Implement the approved plan, report deviations | Scoped writes and shell |
| Verifier | Independent tests and acceptance result | Validation shell only |
| Reviewer | Independent correctness, risk, security and completeness review | Read only |
| wshobson-router | Domain classification and specialist selection only | Catalog metadata read only |

Compose a functional role with a selected specialist profile and, when useful, a skill. A specialist never becomes a permanent core role. The host project's `AGENTS.md` and authorization boundaries still apply.
