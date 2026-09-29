"""Rank marketplace metadata for a functional role and task.

CLI: python router.py --input request.json [--catalog catalog.json]
or:  echo '{"functional_role":"Analyst","task":"..."}' | python router.py

This deterministic shortlist supports model classification by the Router agent:
on low confidence or conflicting domains, the model checks the shortlist and
the task before selecting. The script never loads specialist prompt bodies.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "references/wshobson-catalog.json"
DOMAINS = {
    "networking": {"network", "networking", "wireguard", "vpn", "dns", "tcp", "udp", "routing", "firewall", "tailscale", "handshake", "proxy", "tls"},
    "python": {"python", "asyncio", "pydantic", "django", "fastapi", "flask", "pytest", "pip"},
    "security": {"security", "authentication", "authorization", "auth", "oauth", "identity", "cryptography", "secrets", "vulnerability"},
    "data": {"sql", "database", "query", "postgres", "postgresql", "mysql", "sqlite", "index", "schema"},
    "ai": {"ai", "llm", "rag", "retrieval", "embedding", "embeddings", "vector", "model", "agents"},
    "debugging": {"debug", "debugging", "bug", "failure", "error", "troubleshoot", "diagnose", "incident"},
    "review": {"review", "reviewer", "audit", "assess", "critique", "inspect"},
}
ALIASES = {
    "wireguard": {"network", "vpn", "tunnel"},
    "tailscale": {"network", "vpn"},
    "handshake": {"network", "protocol"},
    "asyncio": {"python", "async"},
    "rag": {"retrieval", "vector", "llm", "ai"},
    "oauth": {"auth", "authentication", "security"},
    "authentication": {"auth", "security"},
    "authorization": {"auth", "security"},
    "sql": {"database", "query"},
    "postgresql": {"postgres", "sql", "database"},
    "review": {"reviewer", "audit"},
    "debug": {"debugger", "debugging", "troubleshoot"},
}
STOPWORDS = {"the", "and", "for", "with", "this", "that", "please", "from", "into", "system", "implementation", "code", "task", "project", "using", "make", "some", "about"}
DIRECT_SYNONYMS = {"authentication": {"auth"}, "authorization": {"auth"}, "wireguard": {"network", "networking", "vpn"}, "rag": {"vector", "retrieval"}, "sql": {"database"}, "asyncio": {"python", "async"}, "debug": {"debugger", "debugging"}, "bug": {"debugger"}}
FRAMEWORK_TERMS = {"fastapi", "django", "flask", "react", "angular", "vue", "kubernetes", "solidity", "temporal"}


def tokens(value: object) -> set[str]:
    return {word for word in re.findall(r"[a-z][a-z0-9]+", str(value).lower().replace("_", "-")) if len(word) > 2 and word not in STOPWORDS}


def expand(query: set[str]) -> set[str]:
    result = set(query)
    for word in query:
        result.update(ALIASES.get(word, set()))
    return result


def domain_for(query: set[str]) -> str:
    scores = {domain: len(query & terms) for domain, terms in DOMAINS.items() if domain not in {"debugging", "review"}}
    if max(scores.values(), default=0):
        return max(scores, key=scores.get)
    actions = {domain: len(query & DOMAINS[domain]) for domain in ("debugging", "review")}
    return max(actions, key=actions.get) if max(actions.values(), default=0) else "general"


def score(entry: dict, query: set[str], role: str) -> float:
    name = tokens(entry.get("name", ""))
    plugin = tokens(entry.get("plugin", ""))
    category = tokens(entry.get("category", ""))
    keywords = set(entry.get("keywords") or [])
    description = tokens(entry.get("description", ""))
    score_value = 6 * len(query & name) + 3 * len(query & plugin) + 2 * len(query & category)
    score_value += 1.5 * len(query & keywords) + 0.5 * len(query & description)
    if role in entry.get("recommended_functional_roles", []):
        score_value += 2
    return score_value


def route(request: dict, catalog: dict) -> dict:
    role = str(request.get("functional_role") or "Analyst").title()
    task = str(request.get("task") or "").strip()
    if not task:
        raise ValueError("task is required")
    context = request.get("context") or ""
    desired_output = request.get("desired_output") or ""
    # Constraints often describe forbidden areas. Never treat them as positive
    # specialist cues (for example "do not touch WireGuard" on a README edit).
    raw = tokens(" ".join(map(str, (task, context, desired_output))))
    direct = set(raw)
    for term in raw:
        direct.update(DIRECT_SYNONYMS.get(term, set()))
    query = expand(raw)
    domain = domain_for(query)
    active_domains = {name for name, terms in DOMAINS.items() if raw & terms}
    if domain != "general":
        active_domains.add(domain)
    concrete_domains = active_domains - {"debugging", "review"}
    # Keep the task's concrete domains as anchors. Generic verbs such as
    # "design" must not pull UI specialists into a RAG architecture route.
    anchors = set().union(*(DOMAINS[name] for name in active_domains)) if active_domains else set()
    skill_anchors = set().union(*(DOMAINS[name] for name in concrete_domains)) if concrete_domains else anchors
    candidates = []
    for entry in catalog.get("entries", []):
        identity_terms = tokens(" ".join((entry.get("name", ""), entry.get("plugin", ""), entry.get("category", ""))))
        if (identity_terms & FRAMEWORK_TERMS) - raw:
            continue
        required = skill_anchors if entry.get("type") == "skill" else anchors
        if required and not (identity_terms & required):
            continue
        match_score = score(entry, query, role)
        match_score += 4 * len(tokens(entry.get("name", "")) & direct)
        candidates.append((match_score, entry))
    agents = sorted((item for item in candidates if item[1].get("type") == "agent" and item[0] > 0), key=lambda item: (-item[0], item[1]["source_path"]))
    skills = sorted((item for item in candidates if item[1].get("type") == "skill" and item[0] > 2), key=lambda item: (-item[0], item[1]["source_path"]))
    primary = agents[0] if agents else None
    # Prefer breadth; duplicate names across plugins are not useful as secondaries.
    secondaries = []
    primary_stem = Path(primary[1]["source_path"]).stem if primary else ""
    for item in agents[1:]:
        if len(secondaries) == 1:
            break
        if item[0] < max(3, (primary[0] if primary else 0) * 0.45):
            break
        entry = item[1]
        stem = Path(entry["source_path"]).stem
        already = {primary_stem} | {Path(other["source_path"]).stem for other in secondaries}
        contextual = entry["plugin"] == primary[1]["plugin"] or bool(tokens(entry["name"]) & direct)
        if stem not in already and contextual:
            secondaries.append(item[1])
    selected_skills = []
    top_skill = skills[0][0] if skills else 0
    for skill_score, entry in skills:
        if len(selected_skills) == 3:
            break
        if skill_score < top_skill * 0.7:
            break
        if (tokens(entry["name"]) & direct) and entry["name"] not in {item["name"] for item in selected_skills}:
            selected_skills.append(entry)
    top = primary[0] if primary else 0
    confidence = "high" if top >= 14 and (len(agents) == 1 or top >= agents[1][0] * 1.25) else "medium" if top >= 7 else "low"
    if confidence == "low":
        reason = "Metadata match is weak; Router agent should classify the task with its model and inspect shortlist metadata before selecting."
    else:
        reason = f"Ranked source-pinned marketplace metadata for {role}; matched task terms and role suitability. Load only selected source paths if needed."
    # Paths disambiguate duplicate names. No prompt body enters this output.
    def identity(entry: dict | None) -> dict | None:
        return {"name": entry["name"], "plugin": entry["plugin"], "source_path": entry["source_path"], "type": entry["type"]} if entry else None
    return {
        "domain": domain,
        "primary_specialist": identity(primary[1]) if primary else None,
        "secondary_specialists": [identity(entry) for entry in secondaries],
        "recommended_skills": [identity(entry) for entry in selected_skills],
        "confidence": confidence,
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="JSON request file; otherwise read stdin")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()
    try:
        request = json.loads(args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read())
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        print(json.dumps(route(request, catalog), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"router error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
