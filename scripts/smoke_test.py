"""Behavioral smoke tests for routing and workflow transitions."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / ".codex/skills/wshobson-router/scripts/router.py"
POLICY = ROOT / ".codex/skills/functional-agent-orchestration/scripts/workflow_policy.py"
BUILDER = ROOT / "scripts/build_wshobson_catalog.py"
VALIDATOR = ROOT / "scripts/validate_structure.py"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def route(role, task, constraints=None):
    request = {"functional_role": role, "task": task, "context": "", "constraints": constraints or [], "desired_output": "specialist metadata"}
    router = load_module(ROUTER, "wshobson_router")
    catalog = json.loads(router.DEFAULT_CATALOG.read_text(encoding="utf-8"))
    return router.route(request, catalog)


def main():
    policy = load_module(POLICY, "workflow_policy")
    cases = [
        ("researcher", "Investigate a WireGuard handshake failure", "network-engineer"),
        ("analyst", "Debug a Python asyncio deadlock", "python"),
        ("executor", "Implement SQL query optimization", "sql"),
        ("reviewer", "Review authentication implementation security", "code-reviewer"),
        ("planner", "Design a RAG system with vector retrieval", "vector-database-engineer"),
    ]
    for role, task, expected in cases:
        answer = route(role, task)
        selected = " ".join(str(x) for x in [answer.get("primary_specialist"), *answer.get("secondary_specialists", []), *answer.get("recommended_skills", [])]).lower()
        assert expected in selected, (task, answer)
        assert len(answer.get("secondary_specialists", [])) <= 2
        assert len(answer.get("recommended_skills", [])) <= 3
        print(f"PASS route: {role} / {expected}")
    excluded = route("executor", "Update README wording", ["Do not touch WireGuard, Tailscale, or firewall configuration"])
    assert excluded["domain"] != "networking", excluded
    assert "network-engineer" not in str(excluded["primary_specialist"]), excluded
    print("PASS route: negative constraints are not expertise cues")
    asyncio_route = route("executor", "Fix Python asyncio double_all returning Task objects instead of doubled integers")
    assert "python" in str(asyncio_route["primary_specialist"]).lower(), asyncio_route
    assert "temporal" not in str(asyncio_route["secondary_specialists"]).lower(), asyncio_route
    print("PASS route: asyncio task excludes unrelated Temporal specialist")
    assert policy.dispatch("analyst")["model"] == "gpt-6-luna"
    assert policy.dispatch("analyst", low_confidence=True, analyst_escalation=1)["reasoning"] == "medium"
    assert policy.dispatch("analyst", low_confidence=True, analyst_escalation=2)["reasoning"] == "high"
    assert policy.dispatch("planner", complexity="complex")["reasoning"] == "high"
    assert policy.dispatch("executor", repeated_failure=True)["model"] == "gpt-6-luna"
    assert policy.failure_destination("executor", "FAIL") == ["analyst", "planner", "executor"]
    assert policy.failure_destination("verifier", "FAIL")[0] == "analyst"
    print("PASS policy: escalation and failure routes")
    builder = load_module(BUILDER, "catalog_builder")
    validator = load_module(VALIDATOR, "structure_validator")
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory)
        subprocess.run(["git", "init", "-q", str(source)], check=True, capture_output=True)
        tracked = source / "tracked.txt"
        tracked.write_text("clean", encoding="utf-8")
        subprocess.run(["git", "-C", str(source), "add", "tracked.txt"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(source), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture"], check=True, capture_output=True)
        assert builder.ensure_clean_source(source)
        tracked.write_text("dirty", encoding="utf-8")
        try:
            builder.ensure_clean_source(source)
        except ValueError:
            pass
        else:
            raise AssertionError("dirty catalog source was accepted")
        invalid = source / "invalid.md"
        invalid.write_text("---\nname: test\ndescription: 'unclosed\n---\n", encoding="utf-8")
        try:
            validator.frontmatter(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid frontmatter was accepted")
    print("PASS source provenance and frontmatter rejection")
    return 0


if __name__ == "__main__":
    sys.exit(main())
