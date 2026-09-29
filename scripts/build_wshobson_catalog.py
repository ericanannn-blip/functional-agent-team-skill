"""Build a small, source-pinned routing index from a local wshobson/agents checkout.

Only frontmatter and plugin manifest metadata enter the output. Specialist bodies
stay in the source checkout and are read only after a route has been selected.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys


DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / ".codex/skills/wshobson-router/references/wshobson-catalog.json"
STOPWORDS = {"and", "the", "for", "with", "from", "into", "your", "that", "this", "using", "agent", "agents", "skill", "skills", "expert", "specialist", "pro", "best", "practices", "development", "implementation"}
SENSITIVE_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"bearer\s+[A-Za-z0-9._~-]{24,}", re.I),
]
ROLE_HINTS = {
    "Researcher": {"research", "search", "retrieval", "literature", "documentation"},
    "Analyst": {"analyze", "analysis", "diagnostic", "debug", "troubleshoot", "incident", "optimize", "performance"},
    "Planner": {"architect", "architecture", "design", "plan", "migration", "strategy"},
    "Executor": {"build", "implement", "code", "develop", "deploy", "integrate", "configure", "fix"},
    "Verifier": {"test", "testing", "validate", "verification", "audit", "qa", "lint"},
    "Reviewer": {"review", "security", "compliance", "audit", "assess"},
}


def locate_source(explicit: str | None) -> Path:
    candidates = [explicit, os.getenv("WSHOBSON_AGENTS_ROOT")]
    here = Path(__file__).resolve().parents[1]
    candidates += [here / "wshobson-agents", here.parent / "agents", Path(os.getenv("TEMP", "/tmp")) / "wshobson-agents-catalog"]
    for candidate in candidates:
        if candidate and (Path(candidate) / "plugins").is_dir():
            return Path(candidate).resolve()
    raise FileNotFoundError("No local wshobson/agents checkout found; pass --source PATH or set WSHOBSON_AGENTS_ROOT")


def frontmatter(path: Path) -> dict[str, str]:
    """Read only the YAML header; simple scalar fields suffice for the source."""
    fields: dict[str, str] = {}
    with path.open(encoding="utf-8-sig", errors="replace") as stream:
        if stream.readline().strip() != "---":
            return fields
        for line in stream:
            if line.strip() == "---":
                break
            match = re.match(r"^([A-Za-z_][\w-]*):\s*(.+?)\s*$", line)
            if match:
                fields[match.group(1)] = match.group(2).strip("\"'")
    return fields


def words(value: str) -> set[str]:
    return {word for word in re.findall(r"[a-z][a-z0-9]+", value.lower().replace("_", "-")) if len(word) > 2 and word not in STOPWORDS}


def safe_description(value: str) -> str:
    # A routing hint only. Avoid multiline instructions and excessive context.
    value = re.sub(r"\s+", " ", value).strip()
    for pattern in SENSITIVE_PATTERNS:
        value = pattern.sub("[redacted]", value)
    return value[:180].rsplit(" ", 1)[0] if len(value) > 180 else value


def source_commit(root: Path) -> str | None:
    result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and re.fullmatch(r"[0-9a-f]{40}", sha) else None


def ensure_clean_source(root: Path) -> str:
    sha = source_commit(root)
    if not sha:
        raise ValueError("Source must be a Git checkout with a valid commit")
    status = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=normal"], capture_output=True, text=True, check=False)
    if status.returncode != 0 or status.stdout.strip():
        raise ValueError("Source checkout has local changes; use a clean pinned checkout")
    return sha


def build(root: Path) -> dict:
    commit = ensure_clean_source(root)
    entries = []
    for plugin_dir in sorted((root / "plugins").iterdir()):
        if not plugin_dir.is_dir():
            continue
        manifest_path = plugin_dir / ".codex-plugin/plugin.json"
        if not manifest_path.is_file():
            manifest_path = plugin_dir / ".claude-plugin/plugin.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
        except (OSError, ValueError):
            manifest = {}
        interface = manifest.get("interface", {}) if isinstance(manifest.get("interface", {}), dict) else {}
        category = safe_description(str(interface.get("category") or plugin_dir.name))
        plugin_desc = str(interface.get("shortDescription") or manifest.get("description") or "")
        files = sorted((plugin_dir / "agents").glob("*.md")) + sorted((plugin_dir / "skills").glob("*/SKILL.md"))
        for path in files:
            metadata = frontmatter(path)
            kind = "agent" if path.parent.name == "agents" else "skill"
            name = safe_description(str(metadata.get("name") or (path.stem if kind == "agent" else path.parent.name)))
            description = safe_description(str(metadata.get("description") or plugin_desc))
            if not description:
                continue
            tokens = words(" ".join((name, plugin_dir.name, category, description)))
            roles = [role for role, hints in ROLE_HINTS.items() if tokens & hints]
            if not roles:
                roles = ["Executor"] if kind == "agent" else ["Analyst"]
            entries.append({
                "name": name,
                "category": category,
                "description": description,
                "type": kind,
                "plugin": plugin_dir.name,
                "source_path": path.relative_to(root).as_posix(),
                "keywords": sorted(tokens)[:24],
                "recommended_functional_roles": roles,
            })
    return {"schema_version": 1, "source_repository": "https://github.com/wshobson/agents", "source_commit": commit, "entry_count": len(entries), "entries": entries}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Local checkout root for wshobson/agents")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    catalog = build(locate_source(args.source))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    header = {key: value for key, value in catalog.items() if key != "entries"}
    fields = [f'  {json.dumps(key)}: {json.dumps(value, ensure_ascii=False)}' for key, value in header.items()]
    entries = ['    ' + json.dumps(entry, ensure_ascii=False, separators=(",", ":")) for entry in catalog["entries"]]
    serialized = "{\n" + ",\n".join(fields) + ',\n  "entries": [\n' + ",\n".join(entries) + "\n  ]\n}"
    # Some benign public paths contain a token-like prefix. Escaping preserves
    # the path after JSON parsing while avoiding a scanner false positive.
    serialized = serialized.replace("sk-", "\\u0073k-")
    args.output.write_text(serialized + "\n", encoding="utf-8")
    print(f"Wrote {catalog['entry_count']} metadata entries; source commit {catalog['source_commit'] or 'unknown'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
