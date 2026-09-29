# Workflow tiers

| Tier | Use | Sequence |
| --- | --- | --- |
| 0 | Deterministic edit | Executor |
| 1 | Normal implementation | Planner → Executor → Verifier |
| 2 | Complex implementation | Researcher → Analyst → Planner → Executor → Verifier → Reviewer |
| 3 | Large or high risk | Orchestrator → independent research → Router → Analyst → Planner → Risk Check → Executor → Verifier → Reviewer → Orchestrator |

Skip stages that do not improve the task. Coding usually routes Planner → Router → Executor → Verifier → Reviewer. Debugging usually routes Researcher → Router → Analyst → Planner → Executor → Verifier. Research can stop after Researcher → Analyst → Orchestrator. Parallelize only independent research, inspection, modules or validation; never shared file edits or dependent mutations. Every planned step declares `parallelizable`.
