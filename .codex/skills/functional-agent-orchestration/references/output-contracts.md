# Output contracts

Return concise YAML-compatible records with these fields:

- Researcher: `task`, `findings[]` (`claim`, `evidence`, `source`, `date`, `confidence`), `contradictions`, `missing_information`.
- Analyst: `problem`, `known_facts`, `hypotheses[]` (`hypothesis`, `evidence_for`, `evidence_against`, `confidence`), `root_cause`, `confidence`, `uncertainties`, `recommended_next_step`, `escalation_required`.
- Planner: `objective`, `scope`, `do_not_touch`, `dependencies`, `steps[]` (`id`, `action`, `agent`, `depends_on`, `parallelizable`), `acceptance_criteria`, `rollback`, `risk_level`.
- Executor: `objective`, `actions_taken`, `files_changed`, `commands_run`, `results`, `deviations_from_plan`, `blocked`, `needs_replan`.
- Verifier: `status` (`PASS`, `FAIL`, `PARTIAL`), `checks[]` (`check`, `expected`, `actual`, `result`), `failures`, `acceptance_criteria_met`, `recommended_destination`.
- Reviewer: `verdict` (`pass`, `pass_with_notes`, `rework_required`), `correctness`, `completeness`, `requirements`, `security`, `maintainability`, `regressions`, `blocking_issues`, `non_blocking_issues`.
- Router: `domain`, `primary_specialist`, `secondary_specialists`, `recommended_skills`, `confidence`, `reason`.

Evidence may contain source paths and dates but never secret values.
