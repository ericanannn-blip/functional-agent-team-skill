---
name: wshobson-router
description: Choose a small set of specialist profiles and optional skills from compact wshobson marketplace metadata for a functional agent task.
---

Accept `functional_role`, `task`, `context`, `constraints`, and `desired_output`. Read only [catalog metadata](references/wshobson-catalog.json) and use [router.py](scripts/router.py) to propose one primary specialist, up to two secondary specialists, and up to three skills. Use model judgment when scores are ambiguous; preserve uncertainty. Load the selected specialist source only after selection from a clean local checkout whose HEAD matches `source_commit`; see [source setup](../../../docs/FUNCTIONAL_AGENTS.md). If unavailable, return metadata-only selection and mark specialist instructions unavailable. Never orchestrate execution or load the full marketplace. Rebuild the catalog with repository `scripts/build_wshobson_catalog.py` when its source commit is stale.
