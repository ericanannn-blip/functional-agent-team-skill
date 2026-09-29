# Permissions

Use native host restrictions where available. Logical minimums: Orchestrator read/delegate; Researcher read/search; Planner, Analyst and Reviewer read; Router catalog metadata read; Executor scoped read/write/shell; Verifier read and validation shell. A role label alone cannot enforce sandbox permissions. For risky operations apply `risk-check` and root `AGENTS.md`; no role can expand authorization.
