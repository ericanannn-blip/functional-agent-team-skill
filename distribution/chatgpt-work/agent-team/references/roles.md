# Team role guide

Choose the smallest useful team. A role is a focused assignment to a real subagent, not a persona to imitate in the main response.

| Role | Assignment | Expected result |
| --- | --- | --- |
| Researcher | Gather relevant, dated source evidence; compare sources and note gaps. | Findings with sources, dates, confidence, contradictions, and missing information. |
| Analyst | Test hypotheses against available evidence; explain likely causes and uncertainty. | Facts, hypotheses, supporting and opposing evidence, confidence, and recommended next step. |
| Planner | Define scope, dependencies, sequence, acceptance criteria, and rollback. | A concise ordered plan; identify which steps can run independently. |
| Executor | Make only the requested, planned changes. | Actions, changed paths, checks run, results, and any deviation or blocker. |
| Verifier | Independently check acceptance criteria and run relevant validation. | PASS, FAIL, or PARTIAL with checks and observed evidence. |
| Reviewer | Inspect completed work for correctness, omissions, risks, and regressions. | Blocking and non-blocking findings with file or evidence references. |

Typical sequences:

- Small deterministic task: Executor → Verifier when a check is useful.
- Normal implementation: Planner → Executor → Verifier.
- Complex implementation: Researcher/Analyst → Planner → Executor → Verifier → Reviewer.
- Research question: Researcher → Analyst, then integrate the supported conclusion.

Only run independent research or inspection in parallel. Do not run dependent work early or let multiple agents edit the same files at once. For low-impact tasks, skip roles that do not improve the result.
