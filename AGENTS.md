# Team Skill repository

This repository contains reusable functional agents and Codex skills. It has no deployment target or domain-specific production configuration.

- Preserve existing work and follow the host project's instructions when these skills are used elsewhere.
- Use `functional-agent-orchestration` for complex multi-step tasks. The Orchestrator manages the lifecycle; `wshobson-router` only selects specialist expertise.
- Give Executor a scoped plan and acceptance criteria. Verify substantial changes before independent review. Send verification failures to Analyst, then Planner before retrying.
- Load the compact specialist catalog first, then only selected source files. Never load the full marketplace into context.
- Role names, model preferences, and skill text do not grant tool permissions or external-action approval. Apply the host's current restrictions and the user's authorization.
- Do not commit secrets, credentials, authentication state, runtime captures, or generated Python caches.
- Keep `main` as the reviewed baseline. Use a feature branch and PR for implementation; do not rewrite history or force-push.
