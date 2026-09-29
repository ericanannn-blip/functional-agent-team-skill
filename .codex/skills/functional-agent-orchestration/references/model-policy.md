# Shared model policy

These are requested dispatch defaults, not a claim that frontmatter enforces a runtime model. Set model and reasoning on delegation when the host supports them; otherwise report the mismatch rather than silently substituting. User and host instructions take priority.

| Role | Default | Escalation |
| --- | --- | --- |
| Orchestrator | GPT-5.6 Sol, high | None automatic |
| Researcher | Luna, high | None automatic |
| Planner | GPT-5.6 Sol, medium | GPT-5.6 Sol, high for complex or high-risk work |
| Analyst | Luna, high | GPT-5.6 Sol, medium; then high when evidence conflicts, confidence is low, or impact is high |
| Executor | Luna, high | Never self-escalate; failure goes to Analyst → Planner → Executor |
| Verifier | Luna, high | Failure goes to Analyst |
| Reviewer | GPT-5.6 Sol, high | None automatic |
| wshobson-router | Luna, high | None automatic |

Use the host's canonical model identifiers (`gpt-5.6-sol`, `gpt-6-luna` if the requested Luna generation is unavailable). The actual run model may differ from this policy; log the effective choice. Do not make model selection a permission bypass.
