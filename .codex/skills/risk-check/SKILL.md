---
name: risk-check
description: Check authorization, reversibility, backups and exposure before destructive, security-sensitive, database or infrastructure mutations.
---

Use before destructive commands, auth or secret handling, firewall changes, database mutation, migrations, volume deletion, infrastructure replacement or irreversible external actions. Read root `AGENTS.md` first. Return `risk`, `reversible`, `backup_available`, `blast_radius`, `secrets_exposed`, `approval_required`, and `safe_alternative`. A check does not grant approval. Prefer a reversible scoped operation and verify a recovery point before authorized high-impact work.
