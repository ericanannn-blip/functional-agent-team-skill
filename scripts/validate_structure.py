"""Validate project functional-agent files and references with stdlib only."""

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".codex" / "skills"
AGENTS = ROOT / ".cursor" / "agents"
ROLES = ["orchestrator", "researcher", "planner", "analyst", "executor", "verifier", "reviewer", "wshobson-router"]
SKILL_NAMES = ["functional-agent-orchestration", "wshobson-router", "risk-check", "editor", "project-state"]
REFERENCES = ["roles.md", "routing.md", "workflows.md", "model-policy.md", "escalation.md", "permissions.md", "output-contracts.md", "failure-handling.md"]


def frontmatter(path):
    data = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", data, re.S)
    if not match:
        raise ValueError(f"Missing YAML frontmatter: {path}")
    fields = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        item = re.fullmatch(r"([a-z][a-z0-9_-]*):[ ]+(.+)", line)
        if not item:
            raise ValueError(f"Unsupported or invalid frontmatter syntax: {path}")
        key, value = item.groups()
        if key in fields or value.startswith(("[", "{", "|", ">", "!", "&", "*")):
            raise ValueError(f"Invalid frontmatter scalar: {path}")
        if value[0] in "\"'" and (len(value) < 2 or value[-1] != value[0]):
            raise ValueError(f"Unclosed frontmatter quote: {path}")
        fields[key] = value.strip().strip('"\'')
    if not fields.get("name") or not fields.get("description"):
        raise ValueError(f"Invalid name/description: {path}")
    return data, fields


def main():
    errors = []
    required = [ROOT / "AGENTS.md", ROOT / "docs" / "FUNCTIONAL_AGENTS.md",
                ROOT / "scripts" / "build_wshobson_catalog.py", ROOT / "scripts" / "smoke_test.py",
                SKILLS / "wshobson-router" / "references" / "wshobson-catalog.json",
                SKILLS / "wshobson-router" / "scripts" / "router.py",
                SKILLS / "functional-agent-orchestration" / "scripts" / "workflow_policy.py",
                SKILLS / "functional-agent-orchestration" / "templates" / "task.yaml",
                SKILLS / "functional-agent-orchestration" / "templates" / "project-state.yaml"]
    required += [AGENTS / f"{name}.md" for name in ROLES]
    required += [SKILLS / name / "SKILL.md" for name in SKILL_NAMES]
    required += [SKILLS / "functional-agent-orchestration" / "references" / name for name in REFERENCES]
    for path in required:
        if not path.is_file():
            errors.append(f"Missing: {path.relative_to(ROOT)}")
    names = {"agent": set(), "skill": set()}
    for kind, paths in [("agent", [AGENTS / f"{x}.md" for x in ROLES]),
                        ("skill", [SKILLS / x / "SKILL.md" for x in SKILL_NAMES])]:
        for path in paths:
            if not path.is_file():
                continue
            try:
                body, fields = frontmatter(path)
                name = fields["name"]
                if name in names[kind]:
                    errors.append(f"Duplicate {kind} name: {name}")
                names[kind].add(name)
                if name != (path.stem if kind == "agent" else path.parent.name):
                    errors.append(f"Name mismatch: {path.relative_to(ROOT)}")
                for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", body):
                    if "://" not in target and not (path.parent / target).resolve().exists():
                        errors.append(f"Broken reference {target} in {path.relative_to(ROOT)}")
            except (OSError, ValueError) as exc:
                errors.append(str(exc))
    for role in ROLES:
        path = AGENTS / f"{role}.md"
        if path.is_file() and "model-policy.md" not in path.read_text(encoding="utf-8"):
            errors.append(f"Model policy reference missing: {role}")
    policy = SKILLS / "functional-agent-orchestration" / "references" / "model-policy.md"
    if policy.is_file() and "Executor" not in policy.read_text(encoding="utf-8"):
        errors.append("Model policy lacks Executor")
    catalog_path = SKILLS / "wshobson-router" / "references" / "wshobson-catalog.json"
    if catalog_path.is_file():
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            if not re.fullmatch(r"[0-9a-f]{40}", catalog.get("source_commit") or ""):
                errors.append("Catalog source commit is missing")
            entries = catalog.get("entries", [])
            if not entries or len(entries) != catalog.get("entry_count"):
                errors.append("Catalog entry count mismatch")
            identities = set()
            for entry in entries:
                identity = tuple(entry.get(k) for k in ("plugin", "type", "source_path"))
                if identity in identities:
                    errors.append(f"Duplicate catalog identity: {identity}")
                identities.add(identity)
                if not all(entry.get(k) for k in ("name", "category", "description", "type", "plugin", "source_path", "keywords", "recommended_functional_roles")):
                    errors.append(f"Incomplete catalog entry: {identity}")
                if entry.get("type") not in {"agent", "skill"}:
                    errors.append(f"Invalid catalog type: {identity}")
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"Invalid catalog: {exc}")
    for error in errors:
        print(f"FAIL {error}")
    print(f"Structure: {'FAIL' if errors else 'PASS'} ({len(required)} required files)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
